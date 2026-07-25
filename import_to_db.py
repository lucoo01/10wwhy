"""将 docs/ 下的"为什么"问题导入 SQLite 单表。

用法:
    python import_to_db.py        # 默认生成 questions.db
    python import_to_db.py -o out.db

数据格式(已实测):
    - 有序号: `1. 问题` 或 `1. [分类] 问题`
    - 无序号: `- 问题`
    - 分类: 百科问答用行内 [分类];专题文件取顶层目录名
    - 章节: ## / ### 标题作为 section
    - 跳过: README.md / DATA_SOURCES.md
"""

import argparse
import re
import sqlite3
from collections import Counter
from pathlib import Path

DOCS_DIR = Path("docs")
DB_PATH = Path("questions.db")
SKIP_FILES = {"README.md", "DATA_SOURCES.md"}
BATCH = 5000

# 行内分类标签,如 "[生命科学] 为什么..." -> ("生命科学", "为什么...")
# 必须命中预定义白名单,否则视为正文(防止 "[生物]..." 这种正文起首被误判为分类)
INLINE_CAT_RE = re.compile(r"^\[([^\]]+)\]\s*(.+)$")
KNOWN_CATEGORIES = frozenset({
    "生命科学", "物理学", "地球与环境", "人体与健康",
    "天文宇宙", "技术与工程", "化学", "心理与社会",
    "历史与人文", "日常生活", "其他", "数学与信息",
})
# 问题行:有序号或无序号列表
Q_RE = re.compile(r"^\s*(?:\d+\.|-)\s+(.+?)\s*$")
# 二级及以下标题作为 section;一级标题(# 文件标题)不作为 section
HEAD_RE = re.compile(r"^\s*#{2,}\s+(.+?)\s*$")


def iter_records(docs_dir: Path):
    for path in sorted(docs_dir.rglob("*.md")):
        if path.name in SKIP_FILES:
            continue
        rel = path.relative_to(docs_dir)
        domain = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        section = None
        source = str(rel).replace("\\", "/")
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.rstrip("\n")
            if line.startswith(">") or line.strip() == "---":
                continue
            h = HEAD_RE.match(line)
            if h:
                section = h.group(1).strip()
                continue
            m = Q_RE.match(line)
            if not m:
                continue
            text = m.group(1).strip()
            cm = INLINE_CAT_RE.match(text)
            # 白名单校验:只有命中已知 12 类才当作分类标签,否则视为正文的一部分
            if cm and cm.group(1).strip() in KNOWN_CATEGORIES:
                category = cm.group(1).strip()
                content = cm.group(2).strip()
            else:
                category = domain
                content = text
            if not content:
                continue
            yield (content, category, domain, section, source)


def build_db(docs_dir: Path, db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            DROP TABLE IF EXISTS questions;
            CREATE TABLE questions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                content      TEXT    NOT NULL,
                category     TEXT    NOT NULL,
                domain       TEXT    NOT NULL,
                section      TEXT,
                source_file  TEXT    NOT NULL
            );
            CREATE INDEX idx_questions_domain   ON questions(domain);
            CREATE INDEX idx_questions_category ON questions(category);
            """
        )

        batch = []
        total = 0
        for rec in iter_records(docs_dir):
            batch.append(rec)
            if len(batch) >= BATCH:
                conn.executemany(
                    "INSERT INTO questions (content, category, domain, section, source_file) "
                    "VALUES (?,?,?,?,?)",
                    batch,
                )
                conn.commit()
                total += len(batch)
                batch.clear()
        if batch:
            conn.executemany(
                "INSERT INTO questions (content, category, domain, section, source_file) "
                "VALUES (?,?,?,?,?)",
                batch,
            )
            conn.commit()
            total += len(batch)
    finally:
        conn.close()
    return total


def print_stats(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        total = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        print(f"\n总计: {total} 条")
        print("\n[按领域 domain 分布]")
        for dom, cnt in cur.execute(
            "SELECT domain, COUNT(*) FROM questions GROUP BY domain ORDER BY 2 DESC"
        ):
            print(f"  {cnt:>7}  {dom}")
        print("\n[百科问答 category 分布]")
        for cat, cnt in cur.execute(
            "SELECT category, COUNT(*) FROM questions "
            "WHERE domain='百科问答' GROUP BY category ORDER BY 2 DESC"
        ):
            print(f"  {cnt:>7}  {cat}")
        # 抽查:不应残留 [分类] 前缀或空内容
        bad = cur.execute(
            "SELECT COUNT(*) FROM questions WHERE content LIKE '[%' OR content=''"
        ).fetchone()[0]
        print(f"\n[异常] 残留 [xxx] 前缀或空 content 行数: {bad} (预期 0)")
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="导入 docs/ 问题到 SQLite")
    ap.add_argument("-o", "--output", default=str(DB_PATH), help="输出数据库路径")
    ap.add_argument("--docs", default=str(DOCS_DIR), help="源 markdown 目录")
    args = ap.parse_args()

    docs_dir = Path(args.docs)
    db_path = Path(args.output)
    if not docs_dir.is_dir():
        raise SystemExit(f"目录不存在: {docs_dir}")

    print(f"扫描目录: {docs_dir}")
    print(f"输出数据库: {db_path}")
    total = build_db(docs_dir, db_path)
    print(f"\n已写入 {total} 条 -> {db_path}")
    print_stats(db_path)


if __name__ == "__main__":
    main()