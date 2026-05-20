#!/usr/bin/env python3
"""重建FTS表"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge.db import get_db


def rebuild_fts():
    """重建FTS表"""

    print("=" * 60)
    print("重建FTS表")
    print("=" * 60)

    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    # 删除旧表
    print("删除旧FTS表...")
    cursor.execute("DROP TABLE IF EXISTS concepts_fts")

    # 创建新表
    print("创建新FTS表...")
    cursor.execute("""
        CREATE VIRTUAL TABLE concepts_fts USING fts5(
            name,
            definition,
            summary,
            content='concepts',
            content_rowid='rowid'
        )
    """)
    conn.commit()

    # FTS5 content表模式会自动同步，但我们需要手动插入触发器

    # 删除旧触发器
    cursor.execute("DROP TRIGGER IF EXISTS concepts_ai")
    cursor.execute("DROP TRIGGER IF EXISTS concepts_ad")
    cursor.execute("DROP TRIGGER IF EXISTS concepts_au")

    # 创建插入触发器
    cursor.execute("""
        CREATE TRIGGER concepts_ai AFTER INSERT ON concepts BEGIN
            INSERT INTO concepts_fts(rowid, name, definition, summary)
            VALUES (new.rowid, new.name, new.definition, new.summary);
        END
    """)

    # 创建删除触发器
    cursor.execute("""
        CREATE TRIGGER concepts_ad AFTER DELETE ON concepts BEGIN
            DELETE FROM concepts_fts WHERE rowid = old.rowid;
        END
    """)

    # 创建更新触发器
    cursor.execute("""
        CREATE TRIGGER concepts_au AFTER UPDATE ON concepts BEGIN
            UPDATE concepts_fts SET name = new.name, definition = new.definition, summary = new.summary
            WHERE rowid = old.rowid;
        END
    """)

    conn.commit()

    # 同步现有数据
    print("同步现有数据...")
    cursor.execute("SELECT COUNT(*) FROM concepts")
    concept_count = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO concepts_fts(rowid, name, definition, summary)
        SELECT rowid, name, definition, summary FROM concepts
    """)
    conn.commit()

    print(f"同步完成，共 {concept_count} 条记录")

    # 测试搜索
    print("\n测试搜索: '分数'")
    cursor.execute("""
        SELECT c.id, c.name, bm25(concepts_fts) as rank
        FROM concepts_fts
        JOIN concepts c ON concepts_fts.rowid = c.rowid
        WHERE concepts_fts MATCH '分数'
        ORDER BY rank
        LIMIT 5
    """)
    results = cursor.fetchall()
    print(f"找到 {len(results)} 个结果:")
    for row in results:
        print(f"  - {row[0]}: {row[1]} (rank: {row[2]:.2f})")

    print("\n测试搜索: '加法'")
    cursor.execute("""
        SELECT c.id, c.name
        FROM concepts_fts
        JOIN concepts c ON concepts_fts.rowid = c.rowid
        WHERE concepts_fts MATCH '加法'
        LIMIT 5
    """)
    results = cursor.fetchall()
    print(f"找到 {len(results)} 个结果:")
    for row in results:
        print(f"  - {row[0]}: {row[1]}")

    print("=" * 60)


if __name__ == "__main__":
    rebuild_fts()