"""多学科支持模块

提供跨学科的知识点管理和检索功能。
"""

from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum

from src.knowledge.crud import SubjectCRUD, ConceptCRUD, BookCRUD
from src.knowledge.db import get_db
from src.knowledge.loader import get_points_by_grade
import logging

logger = logging.getLogger(__name__)


class Subject(str, Enum):
    """学科枚举"""
    MATH = "math"
    CHINESE = "chinese"
    ENGLISH = "english"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    HISTORY = "history"
    GEOGRAPHY = "geography"


@dataclass
class SubjectInfo:
    """学科信息"""
    id: str
    name: str
    name_en: str | None
    phase: str | None
    point_count: int


class MultiSubjectService:
    """多学科服务"""

    def __init__(self):
        self._db = get_db()
        self._cache: dict[str, SubjectInfo] = {}

    def get_supported_subjects(self) -> list[SubjectInfo]:
        """获取支持的学科列表

        Returns:
            list[SubjectInfo]: 学科信息列表
        """
        subjects = SubjectCRUD.list_all()

        conn = self._db.connect()
        cursor = conn.cursor()

        results = []
        for subject in subjects:
            # 统计该学科的知识点数量
            cursor.execute(
                "SELECT COUNT(*) FROM concepts WHERE id LIKE ?",
                (f"{subject.id}_%",)
            )
            count = cursor.fetchone()[0]

            info = SubjectInfo(
                id=subject.id,
                name=subject.name,
                name_en=subject.name_en,
                phase=subject.phase,
                point_count=count
            )
            self._cache[subject.id] = info
            results.append(info)

        return results

    def get_subject_info(self, subject_id: str) -> Optional[SubjectInfo]:
        """获取指定学科的信息

        Args:
            subject_id: 学科ID

        Returns:
            SubjectInfo: 学科信息，不存在返回None
        """
        if subject_id in self._cache:
            return self._cache[subject_id]

        subject = SubjectCRUD.get(subject_id)
        if not subject:
            return None

        # 统计知识点
        conn = self._db.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM concepts WHERE id LIKE ?",
            (f"{subject_id}_%",)
        )
        count = cursor.fetchone()[0]

        info = SubjectInfo(
            id=subject.id,
            name=subject.name,
            name_en=subject.name_en,
            phase=subject.phase,
            point_count=count
        )

        self._cache[subject_id] = info
        return info

    def get_concepts_by_subject(
        self,
        subject_id: str,
        grade: Optional[int] = None
    ) -> list[dict]:
        """按学科获取知识点

        Args:
            subject_id: 学科ID
            grade: 年级筛选

        Returns:
            list[dict]: 知识点列表
        """
        conn = self._db.connect()
        cursor = conn.cursor()

        if grade is not None:
            cursor.execute(
                """SELECT * FROM concepts
                   WHERE id LIKE ?
                   ORDER BY name""",
                (f"{subject_id}_g{grade}_%",)
            )
        else:
            cursor.execute(
                """SELECT * FROM concepts
                   WHERE id LIKE ?
                   ORDER BY id""",
                (f"{subject_id}_%",)
            )

        results = []
        for row in cursor.fetchall():
            data = dict(row)
            results.append(data)

        return results

    def cross_subject_search(
        self,
        query: str,
        subjects: Optional[list[str]] = None,
        limit_per_subject: int = 3
    ) -> dict[str, list[dict]]:
        """跨学科搜索

        Args:
            query: 搜索查询
            subjects: 指定学科列表，None表示所有学科
            limit_per_subject: 每个学科返回的数量

        Returns:
            dict[str, list[dict]]: 按学科分组的结果
        """
        if subjects is None:
            subjects = [s.id for s in SubjectCRUD.list_all()]

        results: dict[str, list[dict]] = {}

        for subject_id in subjects:
            # 简单的模糊匹配
            conn = self._db.connect()
            cursor = conn.cursor()

            cursor.execute(
                """SELECT * FROM concepts
                   WHERE id LIKE ? AND (name LIKE ? OR definition LIKE ?)
                   ORDER BY name
                   LIMIT ?""",
                (f"{subject_id}_%", f"%{query}%", f"%{query}%", limit_per_subject)
            )

            subject_results = []
            for row in cursor.fetchall():
                data = dict(row)
                subject_results.append(data)

            if subject_results:
                results[subject_id] = subject_results

        return results

    def get_related_concepts(
        self,
        concept_id: str,
        limit: int = 5
    ) -> list[dict]:
        """获取相关知识点的跨学科推荐

        Args:
            concept_id: 知识点ID
            limit: 返回数量

        Returns:
            list[dict]: 相关知识点列表
        """
        from src.knowledge.service import get_knowledge_service

        service = get_knowledge_service()
        detail = service.get_knowledge_detail(concept_id)

        if not detail:
            return []

        # 获取当前学科
        current_subject = detail.id.split("_")[0] if "_" in detail.id else "math"

        results = []

        # 1. 同学科的前置/后续知识点
        for prereq_id in detail.prerequisites[:limit // 2]:
            prereq_detail = service.get_knowledge_detail(prereq_id)
            if prereq_detail:
                results.append({
                    "id": prereq_detail.id,
                    "name": prereq_detail.name,
                    "relation": "前置知识",
                    "subject": current_subject
                })

        for dep_id in detail.dependents[:limit // 2]:
            dep_detail = service.get_knowledge_detail(dep_id)
            if dep_detail:
                results.append({
                    "id": dep_detail.id,
                    "name": dep_detail.name,
                    "relation": "后续学习",
                    "subject": current_subject
                })

        # 2. 跨学科相关知识点（基于关键词匹配）
        if len(results) < limit:
            keywords = detail.name.split()[:3]

            conn = self._db.connect()
            cursor = conn.cursor()

            for keyword in keywords:
                cursor.execute(
                    """SELECT id, name FROM concepts
                       WHERE id NOT LIKE ?
                       AND (name LIKE ? OR definition LIKE ?)
                       LIMIT 2""",
                    (f"{current_subject}_%", f"%{keyword}%", f"%{keyword}%")
                )

                for row in cursor.fetchall():
                    if len(results) >= limit:
                        break

                    subject_id = row[0].split("_")[0] if "_" in row[0] else "unknown"
                    results.append({
                        "id": row[0],
                        "name": row[1],
                        "relation": "跨学科相关",
                        "subject": subject_id
                    })

        return results[:limit]

    def get_cross_grade_progress(
        self,
        subject_id: str,
        mastered_ids: set[str]
    ) -> dict[int, dict]:
        """获取跨年级进度

        Args:
            subject_id: 学科ID
            mastered_ids: 已掌握的知识点ID集合

        Returns:
            dict[int, dict]: 按年级分组的进度信息
        """
        conn = self._db.connect()
        cursor = conn.cursor()

        progress: dict[int, dict] = {}

        for grade in range(1, 10):
            cursor.execute(
                "SELECT COUNT(*) FROM concepts WHERE id LIKE ?",
                (f"{subject_id}_g{grade}_%",)
            )
            total = cursor.fetchone()[0]

            if total == 0:
                continue

            cursor.execute(
                """SELECT COUNT(*) FROM concepts
                   WHERE id LIKE ? AND id IN ({})""".format(
                       ",".join(["?" for _ in mastered_ids]) if mastered_ids else "NULL"
                   ),
                (f"{subject_id}_g{grade}_%",) + tuple(mastered_ids) if mastered_ids else (f"{subject_id}_g{grade}_%",)
            )

            # 简化处理，计算 mastered
            mastered = sum(1 for mid in mastered_ids if mid.startswith(f"{subject_id}_g{grade}_"))

            progress[grade] = {
                "total": total,
                "mastered": mastered,
                "rate": mastered / total if total > 0 else 0
            }

        return progress


# 默认服务实例
_default_service: Optional[MultiSubjectService] = None


def get_multisubject_service() -> MultiSubjectService:
    """获取默认多学科服务实例"""
    global _default_service
    if _default_service is None:
        _default_service = MultiSubjectService()
    return _default_service


__all__ = [
    "Subject",
    "SubjectInfo",
    "MultiSubjectService",
    "get_multisubject_service",
]