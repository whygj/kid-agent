#!/usr/bin/env python3
"""全文搜索索引同步脚本

修复 concepts_fts 表与 concepts 表的同步问题。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge.db import get_db


def sync_fts():
    """同步FTS索引"""

    print("=" * 60)
    print("全文搜索索引同步")
    print("=" * 60)

    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    # 检查当前状态
    cursor.execute("SELECT COUNT(*) FROM concepts")
    concept_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM concepts_fts")
    fts_count = cursor.fetchone()[0]

    print(f"\n知识点数量: {concept_count}")
    print(f"FTS索引数量: {fts_count}")

    if concept_count == fts_count:
        print("\n索引已同步，无需处理")
        return

    print(f"\n需要同步 {concept_count - fts_count} 条记录")

    # 删除旧索引
    print("\n删除旧索引...")
    cursor.execute("DELETE FROM concepts_fts")
    conn.commit()

    # 重建索引
    print("重建索引...")
    cursor.execute("""
        INSERT INTO concepts_fts (concept_id, name, definition, summary)
        SELECT id, name, definition, summary FROM concepts
    """)
    conn.commit()

    # 验证
    cursor.execute("SELECT COUNT(*) FROM concepts_fts")
    new_fts_count = cursor.fetchone()[0]

    print(f"\nFTS索引数量: {new_fts_count}")

    if new_fts_count == concept_count:
        print("同步完成！")
    else:
        print(f"警告：索引数量不匹配 ({new_fts_count} != {concept_count})")

    print("=" * 60)


def test_fts_search(query: str):
    """测试全文搜索"""

    print(f"\n测试搜索: '{query}'")

    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.name, bm25(concepts_fts) as rank
        FROM concepts_fts
        JOIN concepts c ON concepts_fts.concept_id = c.id
        WHERE concepts_fts MATCH ?
        ORDER BY rank
        LIMIT 5
    """, (query,))

    results = cursor.fetchall()

    if not results:
        print("  未找到结果")
        return

    for row in results:
        print(f"  - {row[0]}: {row[1]} (rank: {row[2]:.2f})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="同步FTS索引")
    parser.add_argument("--test", type=str, help="测试搜索")
    args = parser.parse_args()

    sync_fts()

    if args.test:
        test_fts_search(args.test)