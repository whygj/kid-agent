"""知识库服务层 - 提供高级业务功能

封装知识点访问、搜索、路径规划等业务逻辑。
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from src.knowledge.crud import (
    ConceptCRUD,
    CommonMistakeCRUD,
    ExerciseCRUD,
    PrerequisiteCRUD,
    Concept,
    CommonMistake,
    Exercise,
)
from src.knowledge.loader import KnowledgePoint, get_point, get_points_by_grade, get_all_points, clear_cache
from src.knowledge.db import get_db

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeDetail:
    """知识点详情（服务层扩展）"""
    id: str
    name: str
    grade: int
    description: str
    difficulty: int
    importance: str
    definition: str
    examples: list[str]
    common_mistakes: list[str]
    aliases: list[str]
    summary: str
    prerequisites: list[str]
    dependents: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class KnowledgeService:
    """知识库服务"""

    def __init__(self):
        """初始化知识库服务"""
        self._db = get_db()
        self._cache: dict[str, KnowledgeDetail] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """确保服务已初始化"""
        if not self._initialized:
            clear_cache()  # 清除缓存确保数据最新
            self._initialized = True

    def get_knowledge_detail(self, point_id: str) -> Optional[KnowledgeDetail]:
        """获取知识点详情（包含定义、常见错误等）

        Args:
            point_id: 知识点ID

        Returns:
            KnowledgeDetail: 知识点详情，不存在返回None
        """
        self._ensure_initialized()

        # 检查缓存
        if point_id in self._cache:
            return self._cache[point_id]

        # 从loader获取基础信息
        point = get_point(point_id)
        if not point:
            return None

        # 从数据库获取扩展信息
        concept = ConceptCRUD.get(point_id)
        if concept:
            definition = concept.definition or ""
            examples = concept.examples or []
            aliases = concept.aliases or []
            summary = concept.summary or ""
            importance = concept.importance or "掌握"
        else:
            definition = point.description or ""
            examples = point.examples or []
            aliases = []
            summary = definition[:200] if definition else ""
            importance = "掌握"

        # 获取常见错误
        mistakes = CommonMistakeCRUD.list_by_concept(point_id)
        common_mistakes = [m.mistake for m in mistakes]

        # 获取前置和后续
        prerequisites = self.get_prerequisite_ids(point_id)
        dependents = self.get_dependent_ids(point_id)

        detail = KnowledgeDetail(
            id=point.id,
            name=point.name,
            grade=point.grade,
            description=point.description,
            difficulty=point.difficulty.value if hasattr(point.difficulty, 'value') else int(point.difficulty),
            importance=importance,
            definition=definition,
            examples=examples,
            common_mistakes=common_mistakes,
            aliases=aliases,
            summary=summary,
            prerequisites=prerequisites,
            dependents=dependents,
            metadata=point.metadata if hasattr(point, 'metadata') else {},
        )

        self._cache[point_id] = detail
        return detail

    def get_common_mistakes(self, point_id: str) -> list[str]:
        """获取知识点的常见错误列表

        Args:
            point_id: 知识点ID

        Returns:
            list[str]: 常见错误列表
        """
        mistakes = CommonMistakeCRUD.list_by_concept(point_id)
        return [m.mistake for m in mistakes]

    def search_knowledge(
        self,
        query: str,
        grade: Optional[int] = None,
        limit: int = 10,
    ) -> list[KnowledgeDetail]:
        """搜索知识点

        Args:
            query: 搜索关键词
            grade: 限定年级
            limit: 返回数量限制

        Returns:
            list[KnowledgeDetail]: 匹配的知识点详情列表
        """
        self._ensure_initialized()

        # 从数据库全文搜索
        concepts = ConceptCRUD.search(query, limit * 2)  # 多获取一些用于筛选

        results = []
        for concept in concepts:
            # 年级筛选
            if grade is not None:
                point = get_point(concept.id)
                if point and point.grade != grade:
                    continue

            detail = self.get_knowledge_detail(concept.id)
            if detail:
                results.append(detail)

            if len(results) >= limit:
                break

        return results

    def get_prerequisite_ids(self, point_id: str) -> list[str]:
        """获取知识点的前置依赖ID列表"""
        return PrerequisiteCRUD.get_prerequisites(point_id)

    def get_dependent_ids(self, point_id: str) -> list[str]:
        """获取依赖该知识点的后续ID列表"""
        return PrerequisiteCRUD.get_dependents(point_id)

    def get_prerequisites_recursive(
        self,
        point_id: str,
        visited: Optional[set[str]] = None,
    ) -> list[str]:
        """递归获取所有前置知识点ID

        Args:
            point_id: 目标知识点ID
            visited: 已访问ID集合（用于递归）

        Returns:
            list[str]: 所有前置知识点ID列表
        """
        if visited is None:
            visited = set()

        if point_id in visited:
            return []

        visited.add(point_id)
        result: list[str] = []

        prereq_ids = self.get_prerequisite_ids(point_id)
        for prereq_id in prereq_ids:
            if prereq_id not in visited:
                result.extend(self.get_prerequisites_recursive(prereq_id, visited))
                if prereq_id not in result:
                    result.append(prereq_id)

        return result

    def get_dependents_recursive(
        self,
        point_id: str,
        visited: Optional[set[str]] = None,
    ) -> list[str]:
        """递归获取所有后续知识点ID

        Args:
            point_id: 起始知识点ID
            visited: 已访问ID集合（用于递归）

        Returns:
            list[str]: 所有后续知识点ID列表
        """
        if visited is None:
            visited = set()

        if point_id in visited:
            return []

        visited.add(point_id)
        result: list[str] = []

        dep_ids = self.get_dependent_ids(point_id)
        for dep_id in dep_ids:
            if dep_id not in visited:
                result.extend(self.get_dependents_recursive(dep_id, visited))
                if dep_id not in result:
                    result.append(dep_id)

        return result

    def get_points_by_grade(self, grade: int) -> list[KnowledgeDetail]:
        """获取指定年级的所有知识点详情

        Args:
            grade: 年级

        Returns:
            list[KnowledgeDetail]: 知识点详情列表
        """
        self._ensure_initialized()
        points = get_points_by_grade(grade)
        return [self.get_knowledge_detail(p.id) for p in points if self.get_knowledge_detail(p.id)]

    def find_learning_path(
        self,
        target_id: str,
        mastered_ids: set[str],
    ) -> list[str]:
        """找到从已掌握到目标知识点的学习路径

        Args:
            target_id: 目标知识点ID
            mastered_ids: 已掌握的知识点ID集合

        Returns:
            list[str]: 学习路径（知识点ID列表）
        """
        # 获取目标的所有前置依赖
        all_prereqs = self.get_prerequisites_recursive(target_id)

        # 找出未掌握的前置依赖
        unmastered_prereqs = [pid for pid in all_prereqs if pid not in mastered_ids]

        # 按依赖关系排序（拓扑排序）
        path = []
        visited = set()

        def add_with_prereqs(pid: str):
            if pid in visited or pid in mastered_ids:
                return

            visited.add(pid)

            # 先添加未掌握的前置
            for prereq_id in self.get_prerequisite_ids(pid):
                if prereq_id not in mastered_ids and prereq_id not in visited:
                    add_with_prereqs(prereq_id)

            if pid not in path:
                path.append(pid)

        for prereq_id in unmastered_prereqs:
            add_with_prereqs(prereq_id)

        path.append(target_id)
        return path

    def get_exercises_for_concept(
        self,
        concept_id: str,
        difficulty: Optional[int] = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """获取关联知识点的习题

        Args:
            concept_id: 知识点ID
            difficulty: 难度等级
            limit: 返回数量限制

        Returns:
            list[dict]: 习题列表
        """
        db = self._db
        conn = db.connect()
        cursor = conn.cursor()

        if difficulty:
            # 按难度筛选
            cursor.execute(
                """SELECT e.* FROM exercises e
                   JOIN relation_tests_concept r ON e.id = r.exercise_id
                   WHERE r.concept_id = ? AND e.difficulty = ?
                   LIMIT ?""",
                (concept_id, difficulty, limit)
            )
        else:
            cursor.execute(
                """SELECT e.* FROM exercises e
                   JOIN relation_tests_concept r ON e.id = r.exercise_id
                   WHERE r.concept_id = ?
                   LIMIT ?""",
                (concept_id, limit)
            )

        import json
        exercises = []
        for row in cursor.fetchall():
            data = dict(row)
            data["options"] = json.loads(data["options"]) if data["options"] else []
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
            exercises.append(data)

        return exercises

    def get_next_learnable_points(
        self,
        grade: int,
        mastered_ids: set[str],
    ) -> list[KnowledgeDetail]:
        """找出下一个可以学习的新知识点

        Args:
            grade: 年级
            mastered_ids: 已掌握的知识点ID集合

        Returns:
            list[KnowledgeDetail]: 可学习的知识点列表
        """
        points = self.get_points_by_grade(grade)
        learnable = []

        for point in points:
            if point.id in mastered_ids:
                continue

            # 检查前置知识是否都已掌握
            prereq_ids = set(self.get_prerequisite_ids(point.id))
            if prereq_ids.issubset(mastered_ids):
                learnable.append(point)

        # 按难度排序
        learnable.sort(key=lambda p: p.difficulty)
        return learnable

    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()
        self._initialized = False
        logger.debug("Knowledge service cache cleared")

    def get_statistics(self) -> dict[str, Any]:
        """获取知识库统计信息"""
        db = self._db
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM concepts")
        total_concepts = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM relation_prerequisite")
        total_relations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM common_mistakes")
        total_mistakes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM exercises")
        total_exercises = cursor.fetchone()[0]

        # 按年级统计
        grade_stats = {}
        for grade in range(1, 10):
            cursor.execute(
                "SELECT COUNT(*) FROM concepts WHERE id LIKE ?",
                (f"math_g{grade}_%",)
            )
            grade_stats[f"grade_{grade}"] = cursor.fetchone()[0]

        return {
            "total_concepts": total_concepts,
            "total_relations": total_relations,
            "total_mistakes": total_mistakes,
            "total_exercises": total_exercises,
            "by_grade": grade_stats,
        }


# 默认服务实例
_default_service: Optional[KnowledgeService] = None


def get_knowledge_service() -> KnowledgeService:
    """获取默认知识库服务实例（懒加载）"""
    global _default_service
    if _default_service is None:
        _default_service = KnowledgeService()
    return _default_service