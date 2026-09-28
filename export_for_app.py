# -*- coding: utf-8 -*-
"""将 questions.db 导出为 App 用的分片 JSON。

输出到 app/src/static/data/：
- index.json: {version, groups: [{id, name, count, shards}]}
- q_<groupId>_<n>.json: 每片 5000 条 [{id, q}]

分组规则：百科问答按 category，其余 domain 按 domain 本身。
可重复运行（数据更新后重跑并重新打包 App 发版）。
"""
import json
import sqlite3
import sys
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "questions.db"
OUT_DIR = Path(__file__).parent / "app" / "src" / "static" / "data"
SHARD_SIZE = 5000


def main():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, content, domain, category FROM questions ORDER BY id"
    ).fetchall()
    conn.close()

    # 分组：百科问答 -> category，其余 -> domain；保持插入顺序
    groups = {}
    for qid, content, domain, category in rows:
        name = category if domain == "百科问答" else domain
        groups.setdefault(name, []).append({"id": qid, "q": content})

    if OUT_DIR.exists():
        for old in OUT_DIR.glob("*.json"):
            old.unlink()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    index = {"version": int(time.time()), "groups": []}
    for gid, (name, items) in enumerate(groups.items(), start=1):
        shards = []
        for n in range(0, len(items), SHARD_SIZE):
            fname = f"q_{gid}_{len(shards)}.json"
            with open(OUT_DIR / fname, "w", encoding="utf-8") as f:
                json.dump(items[n:n + SHARD_SIZE], f, ensure_ascii=False, separators=(",", ":"))
            shards.append(fname)
        index["groups"].append({"id": gid, "name": name, "count": len(items), "shards": shards})

    with open(OUT_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)

    total = sum(g["count"] for g in index["groups"])
    print(f"导出完成：{len(index['groups'])} 个分组，共 {total} 条")
    for g in index["groups"]:
        print(f"  [{g['id']}] {g['name']}: {g['count']} 条, {len(g['shards'])} 片")
    return 0 if total == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
