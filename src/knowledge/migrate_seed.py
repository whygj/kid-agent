"""知识点迁移脚本

将 math_g3g5.py 中的30个知识点迁移到知识库数据库。
"""

import logging
from typing import Optional

from src.knowledge.math_g3g5 import ALL_POINTS, KnowledgePoint
from src.knowledge.db import get_db, init_knowledge_db
from src.knowledge.crud import (
    Book, Concept, CommonMistake, Prerequisite,
    ConceptCRUD, CommonMistakeCRUD, PrerequisiteCRUD,
    generate_id,
)

logger = logging.getLogger(__name__)


def _map_grade_to_book(grade: int) -> str:
    """将年级映射到教材ID（上学期）

    Args:
        grade: 年级 (3, 4, 5)

    Returns:
        str: 教材ID，格式 math_3上_rjb
    """
    return f"math_{grade}上_rjb"


def _create_default_sections() -> None:
    """创建默认章节结构（每个年级一个章节）"""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    section_map = {}

    for grade in [3, 4, 5]:
        book_id = _map_grade_to_book(grade)
        chapter_id = f"math_{grade}上_ch01"
        section_id = f"math_{grade}上_ch01_s01"

        # 章级
        cursor.execute(
            """INSERT OR IGNORE INTO sections (id, book_id, parent_id, title, depth, order_index)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (chapter_id, book_id, None, f"第{grade}年级数学", 0, 1)
        )

        # 节级
        cursor.execute(
            """INSERT OR IGNORE INTO sections (id, book_id, parent_id, title, depth, order_index)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (section_id, book_id, chapter_id, "知识点", 1, 1)
        )

        section_map[grade] = section_id

    conn.commit()
    logger.info(f"Created default sections for grades 3, 4, 5")
    return section_map


def _map_point_to_concept(point: KnowledgePoint, section_id: str) -> Concept:
    """将知识点转换为Concept对象

    Args:
        point: 原知识点对象
        section_id: 所属章节ID

    Returns:
        Concept: 知识库概念对象
    """
    # 生成新的符合规范的ID: math_3上_*
    grade_suffix = {3: "3上", 4: "4上", 5: "5上"}
    new_id = f"math_{grade_suffix[point.grade]}_{point.id.split('_')[-1]}"

    return Concept(
        id=new_id,
        name=point.name,
        section_id=section_id,
        definition=point.description,
        importance=_map_difficulty_to_importance(point.difficulty.value),
        examples=point.examples,
        summary=_generate_summary(point),
        metadata={
            "original_id": point.id,
            "grade": point.grade,
            "difficulty": point.difficulty.value,
            "subject": point.subject,
        },
        created_by="migrate_seed.py",
    )


def _map_difficulty_to_importance(difficulty: int) -> str:
    """将难度映射到重要性等级"""
    mapping = {
        1: "了解",
        2: "理解",
        3: "掌握",
        4: "精通",
        5: "精通",
    }
    return mapping.get(difficulty, "掌握")


def _generate_summary(point: KnowledgePoint) -> str:
    """生成知识点摘要"""
    if point.description:
        return point.description[:200]
    return f"{point.name} - {point.subject}{point.grade}年级"


def _create_id_mapping(grade: int) -> dict[str, str]:
    """创建旧ID到新ID的映射

    Args:
        grade: 年级

    Returns:
        dict: {old_id: new_id}
    """
    grade_suffix = {3: "3上", 4: "4上", 5: "5上"}
    mapping = {}
    for point in ALL_POINTS:
        if point.grade == grade:
            new_id = f"math_{grade_suffix[point.grade]}_{point.id.split('_')[-1]}"
            mapping[point.id] = new_id
    return mapping


def migrate_points(force: bool = False) -> dict[str, int]:
    """迁移知识点到知识库

    Args:
        force: 是否强制重建数据库

    Returns:
        dict: 迁移统计 {concepts, mistakes, prerequisites}
    """
    # 初始化数据库
    init_knowledge_db(force=force)

    # 创建默认章节结构
    _create_default_sections()

    # 创建ID映射
    id_mapping = {}
    for grade in [3, 4, 5]:
        id_mapping.update(_create_id_mapping(grade))

    # 统计信息
    stats = {"concepts": 0, "mistakes": 0, "prerequisites": 0}

    logger.info("Starting knowledge points migration...")

    # 遍历并迁移每个知识点
    for point in ALL_POINTS:
        new_id = id_mapping.get(point.id)
        if not new_id:
            logger.warning(f"No mapping found for point {point.id}, skipping")
            continue

        # 获取章节ID
        section_id = f"math_{point.grade}上_ch01_s01"

        # 转换为Concept
        concept = _map_point_to_concept(point, section_id)
        concept.id = new_id

        # 检查是否已存在
        existing = ConceptCRUD.get(new_id)
        if existing and not force:
            logger.debug(f"Concept {new_id} already exists, skipping")
            continue

        # 创建/更新概念
        if existing:
            ConceptCRUD.update(new_id, {
                "name": concept.name,
                "definition": concept.definition,
                "importance": concept.importance,
                "examples": concept.examples,
                "summary": concept.summary,
            })
            logger.debug(f"Updated concept: {new_id} - {concept.name}")
        else:
            ConceptCRUD.create(concept)
            logger.info(f"Created concept: {new_id} - {concept.name}")
            stats["concepts"] += 1

        # 迁移常见错误
        if point.common_mistakes:
            for mistake in point.common_mistakes:
                mistake_obj = CommonMistake(
                    id=generate_id("mistake"),
                    concept_id=new_id,
                    mistake=mistake,
                )
                CommonMistakeCRUD.create(mistake_obj)
                stats["mistakes"] += 1

        # 迁移前置依赖
        if point.prerequisites:
            for old_prereq_id in point.prerequisites:
                new_prereq_id = id_mapping.get(old_prereq_id)
                if new_prereq_id:
                    prereq = Prerequisite(
                        source_id=new_prereq_id,
                        target_id=new_id,
                        strength=1.0,
                    )
                    PrerequisiteCRUD.add(prereq)
                    stats["prerequisites"] += 1
                else:
                    logger.warning(f"Prerequisite {old_prereq_id} not found for {new_id}")

    logger.info(f"Migration completed: {stats}")
    return stats


def verify_migration() -> dict[str, int]:
    """验证迁移结果

    Returns:
        dict: 验证统计
    """
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM concepts")
    concept_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM common_mistakes")
    mistake_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relation_prerequisite")
    prereq_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relation_tests_concept")
    exercise_rel_count = cursor.fetchone()[0]

    # 按年级统计
    grade_stats = {}
    for grade in [3, 4, 5]:
        cursor.execute(
            """SELECT COUNT(*) FROM concepts c
               JOIN sections s ON c.section_id = s.id
               WHERE s.id LIKE ?""",
            (f"math_{grade}上_%",)
        )
        grade_stats[f"grade_{grade}"] = cursor.fetchone()[0]

    return {
        "total_concepts": concept_count,
        "total_mistakes": mistake_count,
        "total_prerequisites": prereq_count,
        "exercise_concept_relations": exercise_rel_count,
        "by_grade": grade_stats,
    }


def print_verification(stats: dict[str, int]) -> None:
    """打印验证结果"""
    logger.info("=" * 50)
    logger.info("迁移验证结果")
    logger.info("=" * 50)
    logger.info(f"  总知识点数:    {stats['total_concepts']}")
    logger.info(f"  总常见错误数:  {stats['total_mistakes']}")
    logger.info(f"  总前置依赖数:  {stats['total_prerequisites']}")
    logger.info(f"  习题关联数:    {stats['exercise_concept_relations']}")
    logger.info("-" * 50)
    logger.info("按年级统计:")
    for grade, count in stats.get("by_grade", {}).items():
        logger.info(f"  {grade}:  {count} 个知识点")
    logger.info("=" * 50)


def main():
    """主函数"""
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    force = "--force" in sys.argv or "-f" in sys.argv

    if force:
        logger.warning("Force mode enabled - database will be rebuilt!")

    try:
        stats = migrate_points(force=force)
        print(f"\n迁移完成: {stats}")

        verify_stats = verify_migration()
        print_verification(verify_stats)

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()