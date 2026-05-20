"""知识点批量导入脚本

将1-9年级的知识点从Python文件导入到知识库数据库。
"""

import json
import logging
from pathlib import Path
from typing import Any

from src.knowledge.db import get_db, init_knowledge_db
from src.knowledge.crud import (
    Book, Concept, Section, Prerequisite, PrerequisiteCRUD,
    CommonMistake, CommonMistakeCRUD, ConceptCRUD,
    generate_id,
)

logger = logging.getLogger(__name__)

# 年级对应的模块和变量名
GRADE_MODULES = {
    1: ("src.knowledge.math_g1g2", "ALL_POINTS"),
    2: ("src.knowledge.math_g1g2", "ALL_POINTS"),
    3: ("src.knowledge.math_g3g5_v2", "GRADE_3_POINTS"),
    4: ("src.knowledge.math_g3g5_v2", "GRADE_4_POINTS"),
    5: ("src.knowledge.math_g3g5_v2", "GRADE_5_POINTS"),
    6: ("src.knowledge.math_g6", "ALL_POINTS"),
    7: ("src.knowledge.math_g7", "ALL_POINTS"),
    8: ("src.knowledge.math_g8g9", "GRADE_8_POINTS"),
    9: ("src.knowledge.math_g8g9", "GRADE_9_POINTS"),
}


def _import_module(module_name: str, var_name: str):
    """动态导入模块"""
    parts = module_name.split(".")
    module = __import__(module_name)
    for part in parts[1:]:
        module = getattr(module, part)
    return getattr(module, var_name)


def _ensure_book_and_section(cursor: dict[str, Any], grade: int, semester: str = "上") -> str:
    """确保教材和章节存在，返回章节ID

    Args:
        cursor: 数据库游标
        grade: 年级
        semester: 学期

    Returns:
        str: 章节ID
    """
    # 教材ID: math_{grade}{semester}_rjb
    book_id = f"math_{grade}{semester}_rjb"
    book_title = f"数学{grade}年级{semester}"

    # 检查教材是否存在
    cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
    if not cursor.fetchone():
        # 创建教材
        book = Book(
            id=book_id,
            subject_id="math",
            grade=grade,
            semester=semester,
            title=book_title,
        )
        cursor.execute(
            """INSERT INTO books (id, subject_id, grade, semester, publisher, version, title)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (book.id, book.subject_id, book.grade, book.semester,
             book.publisher, book.version, book.title),
        )
        logger.info(f"Created book: {book_id}")

    # 章节ID: math_{grade}{semester}_ch01_s01
    chapter_id = f"math_{grade}{semester}_ch01"
    section_id = f"math_{grade}{semester}_ch01_s01"

    # 检查章节是否存在
    cursor.execute("SELECT id FROM sections WHERE id = ?", (chapter_id,))
    if not cursor.fetchone():
        # 创建章
        cursor.execute(
            """INSERT OR IGNORE INTO sections (id, book_id, parent_id, title, depth, order_index)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (chapter_id, book_id, None, f"第{grade}年级", 0, 1)
        )

    cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
    if not cursor.fetchone():
        # 创建节
        cursor.execute(
            """INSERT OR IGNORE INTO sections (id, book_id, parent_id, title, depth, order_index)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (section_id, book_id, chapter_id, "知识点", 1, 1)
        )
        logger.info(f"Created section: {section_id}")

    return section_id


def _convert_point_to_concept(point, section_id: str, id_map: dict[str, str], cursor: Any, difficulty_map: dict) -> Concept | None:
    """将知识点数据转换为Concept对象

    Args:
        point: 知识点对象
        section_id: 章节ID
        id_map: ID映射字典
        cursor: 数据库游标
        difficulty_map: 难度映射字典

    Returns:
        Concept | None: 转换后的概念对象，如果已存在则返回None
    """
    # 生成新的ID: math_g{grade}_{num}
    try:
        point_id_num = point.id.split("_")[-1]
        new_id = f"math_g{point.grade}_{point_id_num.zfill(3)}"
    except:
        # 如果ID格式不同，使用hash
        import hashlib
        new_id = f"math_g{point.grade}_" + hashlib.md5(point.id.encode()).hexdigest()[:8]

    # 解析难度映射到重要性
    difficulty = getattr(point, "difficulty", 3)
    if isinstance(difficulty, int):
        importance = difficulty_map.get(difficulty, "掌握")
    else:
        # 可能是枚举类型
        importance = difficulty_map.get(difficulty.value if hasattr(difficulty, 'value') else 3, "掌握")

    # 检查是否已存在
    cursor.execute("SELECT id FROM concepts WHERE id = ?", (new_id,))
    if cursor.fetchone():
        return None

    # 处理描述
    description = getattr(point, "description", "")
    if not description:
        description = getattr(point, "summary", "")
    if not description:
        description = point.name

    return Concept(
        id=new_id,
        name=point.name,
        section_id=section_id,
        definition=description,
        importance=importance,
        formula=getattr(point, "formula", None),
        aliases=getattr(point, "aliases", []),
        examples=getattr(point, "examples", []),
        summary=description[:200] if description else None,
        metadata={
            "grade": point.grade,
            "original_id": point.id,
            "category": getattr(point, "category", "通用"),
        },
        created_by="import_points.py",
    )


def import_grade(grade: int, force: bool = False) -> dict[str, int]:
    """导入指定年级的知识点

    Args:
        grade: 年级 (1-9)
        force: 是否覆盖已存在的数据

    Returns:
        dict: 统计信息
    """
    if grade not in GRADE_MODULES:
        raise ValueError(f"不支持年级 {grade}")

    module_name, var_name = GRADE_MODULES[grade]
    logger.info(f"Loading {module_name}.{var_name}...")

    # 初始化数据库
    init_knowledge_db(force=force)

    # 统计信息
    stats = {
        "grade": grade,
        "total": 0,
        "created": 0,
        "skipped": 0,
        "prerequisites": 0,
        "mistakes": 0,
    }

    # 难度映射
    difficulty_map = {
        1: "了解",
        2: "理解",
        3: "掌握",
        4: "精通",
        5: "精通",
    }

    # 导入模块
    points = _import_module(module_name, var_name)

    # 用于ID映射（用于处理前置依赖）
    id_map = {}

    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    try:
        # 确保章节存在
        section_id = _ensure_book_and_section(cursor, grade, "上")
        conn.commit()

        for point in points:
            stats["total"] += 1

            # 转换并创建概念
            concept = _convert_point_to_concept(point, section_id, id_map, cursor, difficulty_map)
            if concept is None:
                stats["skipped"] += 1
                continue

            # 保存ID映射
            id_map[point.id] = concept.id

            # 创建概念
            try:
                ConceptCRUD.create(concept)
                stats["created"] += 1
                logger.debug(f"Created concept: {concept.id} - {concept.name}")
            except Exception as e:
                logger.warning(f"Failed to create concept {concept.id}: {e}")
                continue

            # 迁移常见错误
            if hasattr(point, "common_mistakes") and point.common_mistakes:
                for mistake in point.common_mistakes:
                    try:
                        mistake_obj = CommonMistake(
                            id=generate_id("mistake"),
                            concept_id=concept.id,
                            mistake=mistake,
                        )
                        CommonMistakeCRUD.create(mistake_obj)
                        stats["mistakes"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to create mistake: {e}")

            # 迁移前置依赖
            if hasattr(point, "prerequisites") and point.prerequisites:
                for old_prereq_id in point.prerequisites:
                    new_prereq_id = id_map.get(old_prereq_id)
                    if new_prereq_id and new_prereq_id != concept.id:
                        try:
                            prereq = Prerequisite(
                                source_id=new_prereq_id,
                                target_id=concept.id,
                            )
                            PrerequisiteCRUD.add(prereq)
                            stats["prerequisites"] += 1
                            logger.debug(f"Added prerequisite: {new_prereq_id} -> {concept.id}")
                        except Exception as e:
                            logger.warning(f"Failed to add prerequisite: {e}")

        conn.commit()
        logger.info(f"Grade {grade} import completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Failed to import grade {grade}: {e}", exc_info=True)
        raise

def import_all_grades(grades: list[int] = None, force: bool = False) -> list[dict]:
    """导入多个年级的知识点

    Args:
        grades: 要导入的年级列表，None表示全部1-9年级
        force: 是否覆盖已存在的数据

    Returns:
        list[dict]: 各年级的统计信息
    """
    if grades is None:
        grades = list(range(1, 10))

    all_stats = []
    for grade in grades:
        try:
            stats = import_grade(grade, force)
            all_stats.append(stats)
        except Exception as e:
            logger.error(f"Failed to import grade {grade}: {e}")
            all_stats.append({
                "grade": grade,
                "error": str(e),
            })

    return all_stats


def verify_import() -> dict:
    """验证导入结果"""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    result = {}

    # 总数统计
    cursor.execute("SELECT COUNT(*) FROM concepts")
    result["total_concepts"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relation_prerequisite")
    result["total_prerequisites"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM common_mistakes")
    result["total_mistakes"] = cursor.fetchone()[0]

    # 按年级统计
    for grade in range(1, 10):
        cursor.execute(
            """SELECT COUNT(*) FROM concepts
               WHERE id LIKE ?""",
            (f"math_g{grade}_%",)
        )
        result[f"grade_{grade}"] = cursor.fetchone()[0]

    # 不要关闭连接 - 使用全局单例
    return result


def print_verification(result: dict) -> None:
    """打印验证结果"""
    print("=" * 50)
    print("知识点导入验证结果")
    print("=" * 50)
    print(f"  总知识点数:    {result.get('total_concepts', 0)}")
    print(f"  总前置依赖数:  {result.get('total_prerequisites', 0)}")
    print(f"  总常见错误数:  {result.get('total_mistakes', 0)}")
    print("-" * 50)
    print("按年级统计:")
    total = 0
    for grade in range(1, 10):
        count = result.get(f"grade_{grade}", 0)
        total += count
        print(f"  {grade}年级:  {count} 个知识点")
    print(f"- 总计: {total} 个知识点")
    print("=" * 50)


def main():
    """主函数"""
    import argparse
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="导入知识点到知识库数据库")
    parser.add_argument(
        "--grade",
        type=int,
        help="导入指定年级 (1-9)，不指定则导入全部",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已存在的数据（需要重建数据库）",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="仅验证不导入",
    )

    args = parser.parse_args()

    if args.verify:
        result = verify_import()
        print_verification(result)
        return

    if args.force:
        logger.warning("Force mode enabled - database will be rebuilt!")

    try:
        if args.grade:
            stats = import_grade(args.grade, force=args.force)
            print(f"\n年级 {args.grade} 导入完成: {stats}")
        else:
            all_stats = import_all_grades(force=args.force)
            print("\n所有年级导入完成:")
            for stats in all_stats:
                if "error" in stats:
                    print(f"  {stats['grade']}年级: 失败 - {stats['error']}")
                else:
                    print(f"  {stats['grade']}年级: 创建 {stats['created']}, 跳过 {stats['skipped']}, "
                          f"前置依赖 {stats['prerequisites']}, 常见错误 {stats['mistakes']}")

        verify_stats = verify_import()
        print_verification(verify_stats)

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()