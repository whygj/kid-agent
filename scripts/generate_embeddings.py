#!/usr/bin/env python3
"""知识点点嵌入向量生成脚本

为知识点生成语义向量，用于智能检索和推荐。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import struct
from typing import Optional

import httpx
from src.knowledge.db import get_db
from src.config.settings import get_config


def get_embedding(text: str, model: str = "text-embedding-v2") -> Optional[list[float]]:
    """获取文本嵌入向量

    Args:
        text: 输入文本
        model: 模型名称

    Returns:
        向量列表或None
    """
    try:
        config = get_config()

        response = httpx.post(
            "https://open.bigmodel.cn/api/paas/v4/embeddings",
            headers={
                "Authorization": f"Bearer {config.zhipu_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "input": text[:8192]  # 限制长度
            },
            timeout=30.0
        )

        response.raise_for_status()
        data = response.json()

        return data["data"][0]["embedding"]

    except Exception as e:
        print(f"  [ERROR] 获取嵌入失败: {e}")
        return None


def float_array_to_binary(vec: list[float]) -> bytes:
    """将浮点数组转换为二进制存储（float32）"""
    return struct.pack(f"{len(vec)}f", *vec)


def generate_all_embeddings(limit: int = None, batch_size: int = 10):
    """为所有知识点生成嵌入向量"""

    print("=" * 60)
    print("知识点嵌入向量生成")
    print("=" * 60)

    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    # 获取需要生成的知识点
    cursor.execute("""
        SELECT id, name, definition, summary
        FROM concepts
        WHERE id NOT IN (SELECT concept_id FROM concept_embeddings)
        ORDER BY id
    """)

    concepts = cursor.fetchall()

    if not concepts:
        print("\n所有知识点已有嵌入向量")
        return

    print(f"\n找到 {len(concepts)} 个知识点需要生成嵌入")

    if limit:
        concepts = concepts[:limit]
        print(f"限制处理前 {limit} 个")

    total = 0
    failed = 0

    for idx in range(0, len(concepts), batch_size):
        batch = concepts[idx:idx + batch_size]

        print(f"\n处理批次 {idx // batch_size + 1}/{(len(concepts) + batch_size - 1) // batch_size}")

        for concept_id, name, definition, summary in batch:
            # 组合文本
            text = f"{name}。{definition or ''}。{summary or ''}"

            print(f"  [{idx + concepts.index(concept) + 1}/{len(concepts)}] {name[:30]}...")

            # 获取嵌入
            embedding = get_embedding(text)

            if not embedding:
                failed += 1
                continue

            # 保存嵌入
            embedding_bytes = float_array_to_binary(embedding)

            cursor.execute("""
                INSERT INTO concept_embeddings (concept_id, embedding, model_name)
                VALUES (?, ?, ?)
            """, (concept_id, embedding_bytes, "text-embedding-v2"))

            conn.commit()
            total += 1

    print("\n" + "=" * 60)
    print(f"完成！生成 {total} 个嵌入向量")
    if failed > 0:
        print(f"失败: {failed} 个")
    print("=" * 60)


def semantic_search(query: str, limit: int = 5):
    """语义搜索"""

    print(f"\n语义搜索: '{query}'")

    # 获取查询嵌入
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("无法生成查询嵌入")
        return

    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    # 获取所有嵌入
    cursor.execute("""
        SELECT ce.concept_id, ce.embedding, c.name, c.summary
        FROM concept_embeddings ce
        JOIN concepts c ON ce.concept_id = c.id
    """)

    results = []
    for row in cursor.fetchall():
        concept_id, embedding_bytes, name, summary = row

        # 解码嵌入
        embedding = struct.unpack(f"{len(embedding_bytes) // 4}f", embedding_bytes)

        # 计算余弦相似度
        similarity = cosine_similarity(query_embedding, embedding)

        results.append({
            "id": concept_id,
            "name": name,
            "summary": summary,
            "score": similarity
        })

    # 排序
    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n找到 {len(results)} 个结果:")
    for r in results[:limit]:
        print(f"  - [{r['id']}] {r['name']} (score: {r['score']:.3f})")
        if r['summary']:
            print(f"    {r['summary'][:50]}...")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算余弦相似度"""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="生成知识点嵌入向量")
    parser.add_argument("--limit", type=int, help="限制处理数量")
    parser.add_argument("--search", type=str, help="执行语义搜索")
    args = parser.parse_args()

    if args.search:
        semantic_search(args.search)
    else:
        generate_all_embeddings(limit=args.limit)