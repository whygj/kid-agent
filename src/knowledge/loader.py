"""知识库统一加载器

优先从数据库加载知识点，fallback 到 Python 文件硬编码数据。
"""

import json
import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from src.knowledge.db import get_db, init_knowledge_db
from src.knowledge.crud import ConceptCRUD, PrerequisiteCRUD
from src.knowledge.math_g3g5 import ALL_POINTS, KnowledgePoint as LegacyKnowledgePoint

logger = logging.getLogger(__name__)


class Difficulty(IntEnum):
    """难度等级"""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
    EXPERT = 5


@dataclass
class KnowledgePoint:
    """知识点数据结构（兼容原有接口）

    数据优先从数据库加载，如果数据库没有则从 Python 文件加载。
    """
    id: str
    name: str
    grade: int
    subject: str = "数学"
    difficulty: Difficulty = Difficulty.MEDIUM
    prerequisites: list[str] = None
    description: str = ""
    examples: list[str] = None
    common_mistakes: list[str] = None
    definition: str = ""  # 从数据库获取
    importance: str = "掌握"  # 从数据库获取

    # 数据库额外字段
    section_id: str | None = None
    formula: str | None = None
    aliases: list[str] | None = None
    summary: str | None = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.examples is None:
            self.examples = []
        if self.common_mistakes is None:
            self.common_mistakes = []
        if self.aliases is None:
            self.aliases = []
        # description 优先使用 definition
        if not self.description and self.definition:
            self.description = self.definition


# 缓存已加载的知识点
_points_cache: dict[str, KnowledgePoint] | None = None
_prereq_cache: dict[str, list[str]] | None = None
_db_initialized: bool = False


def _ensure_db() -> bool:
    """确保数据库已初始化"""
    global _db_initialized
    if not _db_initialized:
        try:
            init_knowledge_db()
            _db_initialized = True
            return True
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}, using fallback")
            return False
    return _db_initialized


def _load_from_db(point_id: str) -> Optional[KnowledgePoint]:
    """从数据库加载知识点"""
    try:
        concept = ConceptCRUD.get(point_id)
        if concept is None:
            return None

        # 解析年级从 ID
        grade = _parse_grade_from_id(point_id)

        # 从 importance 映射到 difficulty
        importance_diff = {
            "了解": Difficulty.EASY,
            "理解": Difficulty.MEDIUM,
            "掌握": Difficulty.HARD,
            "精通": Difficulty.VERY_HARD,
        }
        difficulty = importance_diff.get(concept.importance, Difficulty.MEDIUM)

        # 加载前置依赖
        prereqs = PrerequisiteCRUD.get_prerequisites(point_id)

        return KnowledgePoint(
            id=concept.id,
            name=concept.name,
            grade=grade,
            subject="数学",
            difficulty=difficulty,
            prerequisites=prereqs,
            description=concept.definition or concept.summary or "",
            examples=concept.examples or [],
            common_mistakes=[],  # 可以单独加载 common_mistakes 表
            definition=concept.definition or "",
            importance=concept.importance,
            section_id=concept.section_id,
            formula=concept.formula,
            aliases=concept.aliases,
            summary=concept.summary,
        )
    except Exception as e:
        logger.debug(f"Failed to load {point_id} from DB: {e}")
        return None


def _parse_grade_from_id(point_id: str) -> int:
    """从 ID 解析年级"""
    # K12-KGraph 格式: math_1a_rjb_cptX, math_bx1_rjb_cptX 等
    if "_1a" in point_id or "_1b" in point_id:
        return 1
    elif "_2a" in point_id or "_2b" in point_id:
        return 2
    elif "_3a" in point_id or "_3b" in point_id:
        return 3
    elif "_4a" in point_id or "_4b" in point_id:
        return 4
    elif "_5a" in point_id or "_5b" in point_id:
        return 5
    elif "_6a" in point_id or "_6b" in point_id:
        return 6
    elif "_7a" in point_id or "_7b" in point_id:
        return 7
    elif "_8a" in point_id or "_8b" in point_id:
        return 8
    elif "_9a" in point_id or "_9b" in point_id:
        return 9
    elif "_bx1" in point_id:
        return 10
    elif "_bx2" in point_id:
        return 11
    elif "_xzxbx1" in point_id:
        return 11
    elif "_xzxbx2" in point_id:
        return 12
    elif "_xzxbx3" in point_id:
        return 12

    # 旧格式: math_g3_001
    if "_g3_" in point_id:
        return 3
    elif "_g4_" in point_id:
        return 4
    elif "_g5_" in point_id:
        return 5

    # 默认 3 年级
    return 3


def _load_all_from_db() -> dict[str, KnowledgePoint]:
    """从数据库加载所有知识点"""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM concepts")
    point_ids = [row[0] for row in cursor.fetchall()]

    points = {}
    for pid in point_ids:
        point = _load_from_db(pid)
        if point:
            points[pid] = point

    logger.info(f"Loaded {len(points)} points from database")
    return points


def get_point(point_id: str) -> Optional[KnowledgePoint]:
    """获取知识点

    优先从数据库加载，如果不存在则从 Python 文件加载。
    """
    global _points_cache

    # 确保数据库已初始化
    _ensure_db()

    # 初始化缓存
    if _points_cache is None:
        _points_cache = _load_all_from_db()

    # 从缓存返回
    if point_id in _points_cache:
        return _points_cache[point_id]

    # Fallback: 从 Python 文件加载
    for legacy_point in ALL_POINTS:
        if legacy_point.id == point_id:
            point = KnowledgePoint(
                id=legacy_point.id,
                name=legacy_point.name,
                grade=legacy_point.grade,
                subject=legacy_point.subject,
                difficulty=legacy_point.difficulty,
                prerequisites=legacy_point.prerequisites,
                description=legacy_point.description,
                examples=legacy_point.examples,
                common_mistakes=legacy_point.common_mistakes,
            )
            _points_cache[point_id] = point
            return point

    return None


def get_points_by_grade(grade: int) -> list[KnowledgePoint]:
    """获取指定年级的所有知识点"""
    global _points_cache

    if _points_cache is None:
        _points_cache = _load_all_from_db()

    # 筛选匹配年级的知识点
    result = []
    for point in _points_cache.values():
        if point.grade == grade:
            result.append(point)

    logger.debug(f"Found {len(result)} points for grade {grade}")
    return result


def get_points_by_difficulty(difficulty: int | Difficulty) -> list[KnowledgePoint]:
    """获取指定难度的知识点"""
    global _points_cache

    if _points_cache is None:
        _points_cache = _load_all_from_db()

    if isinstance(difficulty, Difficulty):
        difficulty = difficulty.value

    return [p for p in _points_cache.values() if p.difficulty.value == difficulty]


def get_all_points() -> list[KnowledgePoint]:
    """获取所有知识点"""
    global _points_cache

    if _points_cache is None:
        _points_cache = _load_all_from_db()

    return list(_points_cache.values())


def get_prerequisites(point_id: str) -> list[str]:
    """获取知识点的前置依赖 ID 列表"""
    global _prereq_cache

    if _prereq_cache is None:
        _prereq_cache = {}

    if point_id not in _prereq_cache:
        # 尝试从数据库加载
        try:
            prereqs = PrerequisiteCRUD.get_prerequisites(point_id)
            if prereqs:
                _prereq_cache[point_id] = prereqs
            else:
                # Fallback: 尝试从知识点对象获取
                point = get_point(point_id)
                if point and point.prerequisites:
                    _prereq_cache[point_id] = point.prerequisites
                else:
                    _prereq_cache[point_id] = []
        except Exception as e:
            logger.debug(f"Failed to load prerequisites for {point_id}: {e}")
            _prereq_cache[point_id] = []

    return _prereq_cache.get(point_id, [])


def get_dependents(source_id: str) -> list[str]:
    """获取依赖该知识点的后续知识点 ID 列表"""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT target_id FROM relation_prerequisite WHERE source_id = ?",
        (source_id,)
    )
    return [row[0] for row in cursor.fetchall()]


def clear_cache() -> None:
    """清空缓存（用于测试或数据更新后）"""
    global _points_cache, _prereq_cache
    _points_cache = None
    _prereq_cache = None
    logger.info("Knowledge cache cleared")


# 导出与 math_g3g5 兼容的接口
ALL_KNOWLEDGE_POINTS: list[KnowledgePoint] | None = None


def get_all_legacy_compatible() -> list[KnowledgePoint]:
    """获取所有知识点（兼容原 ALL_POINTS 接口）"""
    global ALL_KNOWLEDGE_POINTS

    if ALL_KNOWLEDGE_POINTS is None:
        ALL_KNOWLEDGE_POINTS = get_all_points()

    return ALL_KNOWLEDGE_POINTS