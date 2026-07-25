"""调用大模型批量审核并修正 questions.db 中的问题。

用法:
    python review_questions.py                       # 全部未审核
    python review_questions.py --limit 200           # 仅前 200 条(评估)
    python review_questions.py --batch-size 50       # 改批次大小(默认 50)
    python review_questions.py --workers 8           # 改并发(默认 4)

环境变量(从 .env 读取):
    CM_API_KEY   - API 密钥
    CM_BASE_URL  - API 基础 URL
    CM_MODEL     - 模型名(cm-code-latest / MiniMax-M2.5 等价)
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    sys.exit("缺少 openai 包,请先: pip install openai")

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # 进度条可选

DB_PATH = Path("questions.db")
FAIL_LOG = Path("review_failures.jsonl")

# ---------- .env 简易加载(不依赖 python-dotenv) ----------

def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


# ---------- 表结构迁移 ----------

def migrate(conn: sqlite3.Connection) -> None:
    """幂等地加上审核相关列。"""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(questions)")}
    alters = []
    if "corrected_content" not in cols:
        alters.append("ALTER TABLE questions ADD COLUMN corrected_content TEXT")
    if "reviewed_at" not in cols:
        alters.append("ALTER TABLE questions ADD COLUMN reviewed_at TIMESTAMP")
    if "review_reason" not in cols:
        alters.append("ALTER TABLE questions ADD COLUMN review_reason TEXT")
    for sql in alters:
        conn.execute(sql)
    if alters:
        conn.commit()


# ---------- Prompt ----------

SYSTEM_PROMPT = """你是一个严谨的中文问题审核员。任务是:逐条判断给定的问题句是否有错,如果有错就修正。

## 判定"有错"的标准(满足任一即可)
1. 病句、语法不通、有翻译腔(明显非中文习惯表达)
2. 不是疑问句(陈述句、标题型短句、不构成提问)
3. 科学事实明显错误(不含合理猜想/开放假设)
4. 表述不可理解、矛盾、明显缺漏

## 严格要求
- 仅修正"问题句"本身,**不要给答案,不要补充解释**
- 保持原意不变,只在必要处做最小修改
- 保持疑问语气(以"为什么/为何/怎么/如何/是什么/有哪些/是否"等疑问形式结尾)
- 修正后必须是中文疑问句,长度与原句接近

## 输出格式
**严格 JSON 数组**,只包含需要修正的条目。**正确的条目不要出现在输出里**(这样省略即代表"原文无误")。

字段名**必须**严格遵守(否则客户端会丢弃):
- `id`: 数字,与输入对应
- `corrected`(或 `content`): 修正后的问题句(任一字段名都可识别)
- `reason`: ≤30 字中文原因(可选)

示例(注意字段名,务必使用 "corrected" 或 "content"):

```json
[{"id": 123, "corrected": "修正后的问题句", "reason": "去除翻译腔"}]
```

- 按输入 id 顺序返回
- reason 简短中文,不超过 30 字
- 若整批都正确,返回 []
- 不要返回任何思考过程、注释、Markdown 包裹(直接 JSON 数组开头)"""


USER_PROMPT_TMPL = """请审核以下 {n} 条问题句。

```json
{items}
```

输出(只返回需要修正的条目,严格 JSON 数组):"""


def build_messages(items: list[tuple[int, str]]) -> list[dict]:
    payload = [{"id": i, "content": c} for i, c in items]
    user = USER_PROMPT_TMPL.format(n=len(items), items=json.dumps(payload, ensure_ascii=False, indent=2))
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


# ---------- JSON 提取(防御 reasoning_content) ----------

_JSON_FENCE = re.compile(r"```(?:json)?\s*([\[{].*?[\]}])\s*```", re.DOTALL)


def extract_json_array(text: str) -> list | None:
    """从 LLM 输出中尽力提取一个 JSON 数组。

    防御:
    - 思考过程干扰(虽然 prompt 已要求,但兜底)
    - 包裹在 ```json ... ``` 中
    - 数组前后有空白/换行
    """
    text = text.strip()
    # 1. 优先尝试 ```json ... ``` 代码块
    m = _JSON_FENCE.search(text)
    if m:
        try:
            v = json.loads(m.group(1))
            return v if isinstance(v, list) else None
        except json.JSONDecodeError:
            pass
    # 2. 直接整段是 JSON
    if text.startswith("["):
        try:
            v = json.loads(text)
            return v if isinstance(v, list) else None
        except json.JSONDecodeError:
            pass
    # 3. 兜底:找第一个 [ 到最后一个 ]
    lb, rb = text.find("["), text.rfind("]")
    if lb != -1 and rb > lb:
        try:
            v = json.loads(text[lb:rb + 1])
            return v if isinstance(v, list) else None
        except json.JSONDecodeError:
            pass
    return None


# ---------- LLM 调用(带指数退避重试) ----------

def call_review(client: OpenAI, model: str, items: list[tuple[int, str]]) -> list[dict]:
    """单次 batch 调用,带重试。返回解析后的 JSON 数组(可能为空),失败抛异常。"""
    messages = build_messages(items)
    last_err = None
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                timeout=90,
            )
            content = resp.choices[0].message.content or ""
            arr = extract_json_array(content)
            if arr is None:
                raise ValueError(f"JSON 解析失败,原始输出前 200 字: {content[:200]!r}")
            return arr
        except Exception as e:
            last_err = e
            wait = 2 ** attempt
            print(f"[重试 {attempt + 1}/3] {type(e).__name__}: {str(e)[:120]}...等待 {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"3 次重试均失败: {last_err}")


# ---------- 核心流程 ----------

def fetch_pending(conn: sqlite3.Connection, limit: int | None) -> list[tuple[int, str]]:
    sql = "SELECT id, content FROM questions WHERE reviewed_at IS NULL ORDER BY id"
    if limit:
        sql += f" LIMIT {limit}"
    return [(r[0], r[1]) for r in conn.execute(sql)]


def chunked(items, n):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def apply_batch(conn: sqlite3.Connection, batch_ids: list[int], parsed: list[dict]) -> dict:
    """把单批结果回写数据库。返回统计 dict。"""
    # id -> (corrected, reason) 索引(只保留 dict 且有 id/corrected 的)
    fixed_map = {}
    parse_failures = 0
    for item in parsed:
        if not isinstance(item, dict):
            parse_failures += 1
            continue
        rid = item.get("id")
        # 兼容 LLM 用 "corrected" 或 "content" 字段名
        corrected = item.get("corrected") or item.get("content")
        reason = item.get("reason", "")
        if not isinstance(rid, int) or not isinstance(corrected, str) or not corrected.strip():
            parse_failures += 1
            continue
        fixed_map[rid] = (corrected.strip(), str(reason)[:60])

    rows = []
    for rid in batch_ids:
        if rid in fixed_map:
            c, r = fixed_map[rid]
            rows.append((c, r, rid))            # 修正
        else:
            rows.append((None, "原文无误", rid)) # 视为正确(corrected_content=NULL → 查询时回退到 content)
    conn.executemany(
        "UPDATE questions SET corrected_content=?, review_reason=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?",
        rows,
    )
    return {
        "fixed": len(fixed_map),
        "ok": len(batch_ids) - len(fixed_map),
        "parse_failures": parse_failures,
    }


def run(db_path: Path, limit: int | None, batch_size: int, workers: int) -> None:
    api_key = os.environ.get("CM_API_KEY")
    base_url = os.environ.get("CM_BASE_URL", "https://zhenze-huhehaote.cmecloud.cn/api/coding/v1")
    model = os.environ.get("CM_MODEL", "cm-code-latest")
    if not api_key:
        sys.exit("缺少 CM_API_KEY 环境变量(请配置 .env)")

    client = OpenAI(api_key=api_key, base_url=base_url)

    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")  # 并发写更稳
    try:
        migrate(conn)

        pending = fetch_pending(conn, limit)
        if not pending:
            print("没有待审核的问题(reviewed_at IS NULL 为空)。")
            return
        print(f"待审核: {len(pending)} 条  batch={batch_size}  workers={workers}")
        batches = list(chunked(pending, batch_size))
        total_batches = len(batches)

        # 进度统计
        tot_ok = tot_fixed = tot_pf = 0
        tot_api_fail = 0

        iterator = as_completed if workers > 1 else None
        if workers == 1:
            bar = tqdm(batches, desc="审核中") if tqdm else batches
            for b in bar:
                items = [(rid, content) for rid, content in b]
                ids = [rid for rid, _ in items]
                try:
                    parsed = call_review(client, model, items)
                    st = apply_batch(conn, ids, parsed)
                    conn.commit()
                    tot_ok += st["ok"]; tot_fixed += st["fixed"]; tot_pf += st["parse_failures"]
                except Exception as e:
                    tot_api_fail += len(items)
                    log_failure(FAIL_LOG, ids, str(e))
                    conn.rollback()
        else:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = {ex.submit(call_review, client, model, [(rid, c) for rid, c in b]): b for b in batches}
                bar = tqdm(as_completed(futures), total=total_batches, desc="审核中") if tqdm else as_completed(futures)
                for fut in bar:
                    b = futures[fut]
                    ids = [rid for rid, _ in b]
                    try:
                        parsed = fut.result()
                        st = apply_batch(conn, ids, parsed)
                        conn.commit()
                        tot_ok += st["ok"]; tot_fixed += st["fixed"]; tot_pf += st["parse_failures"]
                    except Exception as e:
                        tot_api_fail += len(b)
                        log_failure(FAIL_LOG, ids, str(e))
                        conn.rollback()

        # 汇总
        total_rows = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        reviewed = conn.execute("SELECT COUNT(*) FROM questions WHERE reviewed_at IS NOT NULL").fetchone()[0]
        print(f"\n===== 完成 =====")
        print(f"数据库总条数: {total_rows}")
        print(f"已审核: {reviewed} ({reviewed / total_rows:.1%})")
        print(f"本轮 ok: {tot_ok}    修正: {tot_fixed}    单条解析失败: {tot_pf}    API 失败整批丢: {tot_api_fail}")
        if FAIL_LOG.exists():
            print(f"失败批次日志: {FAIL_LOG}")
    finally:
        conn.close()


def log_failure(path: Path, ids: list[int], err: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ids": ids, "error": err[:500]}, ensure_ascii=False) + "\n")


def main() -> None:
    load_env(Path(".env"))
    ap = argparse.ArgumentParser(description="批量审核并修正 questions.db 中的问题")
    ap.add_argument("-d", "--db", default=str(DB_PATH), help="数据库路径")
    ap.add_argument("--limit", type=int, default=None, help="最多处理 N 条(默认全部未审核)")
    ap.add_argument("--batch-size", type=int, default=50, help="每批提交给 LLM 的条数")
    ap.add_argument("--workers", type=int, default=4, help="并发线程数")
    args = ap.parse_args()

    run(Path(args.db), args.limit, args.batch_size, args.workers)


if __name__ == "__main__":
    main()