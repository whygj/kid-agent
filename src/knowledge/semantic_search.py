"""语义搜索模块

提供基于向量嵌入的知识点语义检索功能。
"""

import httpx
import struct
from typing import Optional, Callable

from src.knowledge.db import get_db
from src.config.settings import get_config
import logging

logger = logging.getLogger(__name__)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算余弦相似度

    Args:
        a: 向量A
        b: 向量B

    Returns:
        float: 相似度分数 0-1
    """
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class EmbeddingClient:
    """嵌入向量客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_config().zhipu_api_key
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
        self.model = "embedding-2"

    async def get_embedding(self, text: str) -> Optional[list[float]]:
        """获取文本嵌入向量

        Args:
            text: 输入文本

        Returns:
            向量列表或None
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": text[:8192]
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]

        except Exception as e:
            logger.error(f"获取嵌入失败: {e}")
            return None

    def get_embedding_sync(self, text: str) -> Optional[list[float]]:
        """同步获取文本嵌入向量"""
        try:
            response = httpx.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": text[:8192]
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]

        except Exception as e:
            logger.error(f"获取嵌入失败: {e}")
            return None


class SemanticSearch:
    """语义搜索服务"""

    def __init__(self):
        self._client = EmbeddingClient()
        self._cache: dict[str, list[float]] = {}

    def search(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.5,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> list[dict]:
        """语义搜索知识点

        Args:
            query: 搜索查询
            limit: 返回数量限制
            threshold: 相似度阈值
            on_progress: 进度回调 (current, total)

        Returns:
            list[dict]: 搜索结果，包含知识点信息和相似度分数
        """
        # 获取查询嵌入
        query_embedding = self._client.get_embedding_sync(query)
        if not query_embedding:
            logger.warning("无法生成查询嵌入")
            return []

        # 从数据库获取所有嵌入
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ce.concept_id, ce.embedding, c.name, c.definition, c.summary
            FROM concept_embeddings ce
            JOIN concepts c ON ce.concept_id = c.id
        """)

        results = []
        total = 0
        for row in cursor.fetchall():
            total += 1
            concept_id, embedding_bytes, name, definition, summary = row

            # 解码嵌入
            embedding = struct.unpack(f"{len(embedding_bytes) // 4}f", embedding_bytes)

            # 计算相似度
            similarity = cosine_similarity(query_embedding, embedding)

            if similarity >= threshold:
                results.append({
                    "id": concept_id,
                    "name": name,
                    "definition": definition,
                    "summary": summary,
                    "score": similarity
                })

            if on_progress and total % 10 == 0:
                on_progress(total, total)

        # 按相似度排序
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]

    def has_embeddings(self) -> bool:
        """检查是否有嵌入数据"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM concept_embeddings")
        count = cursor.fetchone()[0]
        return count > 0

    def get_embedding_count(self) -> int:
        """获取嵌入数量"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM concept_embeddings")
        return cursor.fetchone()[0]


def search_hybrid(
    query: str,
    limit: int = 5,
    semantic_weight: float = 0.7
) -> list[dict]:
    """混合搜索（全文 + 语义）

    Args:
        query: 搜索查询
        limit: 返回数量限制
        semantic_weight: 语义搜索权重 (0-1)

    Returns:
        list[dict]: 搜索结果
    """
    from src.knowledge.crud import ConceptCRUD

    # 全文搜索
    fts_results = ConceptCRUD.search(query, limit * 2)

    # 语义搜索（如果有嵌入）
    semantic = SemanticSearch()
    sem_results = []

    if semantic.has_embeddings():
        sem_results = semantic.search(query, limit * 2)

    # 合并结果
    combined: dict[str, dict] = {}

    for concept in fts_results:
        combined[concept.id] = {
            "id": concept.id,
            "name": concept.name,
            "definition": concept.definition,
            "summary": concept.summary,
            "fts_score": 1.0,
            "semantic_score": 0.0,
        }

    for result in sem_results:
        if result["id"] in combined:
            combined[result["id"]]["semantic_score"] = result["score"]
        else:
            combined[result["id"]] = {
                "id": result["id"],
                "name": result["name"],
                "definition": result["definition"],
                "summary": result["summary"],
                "fts_score": 0.0,
                "semantic_score": result["score"],
            }

    # 计算综合分数
    for item in combined.values():
        item["score"] = (
            item["fts_score"] * (1 - semantic_weight) +
            item["semantic_score"] * semantic_weight
        )

    # 排序
    sorted_results = sorted(
        combined.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    return sorted_results[:limit]


__all__ = [
    "cosine_similarity",
    "EmbeddingClient",
    "SemanticSearch",
    "search_hybrid",
]