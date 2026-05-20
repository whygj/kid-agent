"""K12-KGraph 数据集导入脚本

从 GitHub 下载 K12-KGraph 数据集并导入到知识库数据库。

GitHub: https://github.com/haolpku/K12-Dataset

数据结构:
- nodes: 节点列表
- edges: 边列表

节点根据 ID 前缀推断类型:
- math_Xa_rjb, phys_Xa_rjb, chem_Xa_rjb, bio_Xa_rjb -> Book (教材)
- _cptX -> Chapter (章)
- _secX -> Section (节)
- 其他有 definition/name -> Concept (概念)
- skill_X -> Skill (技能)
- exercise_X -> Exercise (习题)

关系类型:
- prerequisites_for -> relation_prerequisite
- relates_to -> relation_related
- is_a -> relation_is_a
- tests_concept -> relation_tests_concept
- tests_skill -> relation_tests_skill
- appears_in, is_part_of -> 结构关系
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from src.knowledge.db import get_db, init_knowledge_db
from src.knowledge.crud import (
    Book, Section, Concept, Skill, Exercise,
    ConceptCRUD, SkillCRUD, ExerciseCRUD,
    PrerequisiteCRUD, ExerciseConceptRelationCRUD, generate_id,
)

logger = logging.getLogger(__name__)


# 学科映射
SUBJECT_MAP = {
    "math": "math",
    "mathematics": "math",
    "phys": "physics",
    "physics": "physics",
    "chem": "chemistry",
    "chemistry": "chemistry",
    "bio": "biology",
    "biology": "biology",
}


def infer_node_type(node_id: str, node: dict) -> str:
    """根据 label 字段推断节点类型"""
    # 优先使用 label 字段
    label = node.get("label", "")
    if label:
        return label

    # 回退到基于 ID 的推断
    node_id = node_id or ""

    # Book 教材: math_7a_rjb, phys_8b_rjb, chem_9a_rjb, bio_10a_rjb
    if re.match(r'^(math|phys|chem|bio)_\d+[ab]_', node_id):
        return "Book"

    # Chapter 章节: math_7a_rjb_cpt1, phys_8b_rjb_cpt2
    if "_cpt" in node_id:
        return "Chapter"

    # Section 节: math_7a_rjb_cpt1_sec1
    if "_sec" in node_id:
        return "Section"

    # Skill 技能: skill_开头
    if node_id.startswith("skill_"):
        return "Skill"

    # Exercise 习题: exercise_开头
    if node_id.startswith("exercise_"):
        return "Exercise"

    # Experiment 实验: experiment_开头
    if node_id.startswith("experiment_"):
        return "Experiment"

    return "Unknown"


def parse_book_id(raw_id: str) -> tuple[str, int, str, str]:
    """解析书籍ID

    示例: math_7a_rjb -> (math, 7, 上, rjb)
    """
    parts = raw_id.split("_")
    if len(parts) >= 3:
        subject_code = parts[0]
        grade_sem = parts[1]
        publisher = "_".join(parts[2:])

        # 解析年级和学期
        if len(grade_sem) >= 2:
            grade_char = grade_sem[0]
            semester_char = grade_sem[1]

            try:
                grade = int(grade_char)
                semester = {"a": "上", "b": "下"}.get(semester_char, "上")
                # 映射学科代码
                subject_id = SUBJECT_MAP.get(subject_code, subject_code)
                return subject_id, grade, semester, publisher
            except (ValueError, IndexError):
                pass

    # 默认值
    return "math", 1, "上", "rjb"


def clean_string(s: str | None) -> str | None:
    """清理字符串"""
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    return s if s else None


def ensure_subject(subject_name: str) -> str:
    """确保学科存在，返回学科ID"""
    subject_id = SUBJECT_MAP.get(subject_name.lower())
    if not subject_id:
        logger.warning(f"Unknown subject: {subject_name}, using 'other'")
        subject_id = "other"

    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM subjects WHERE id = ?", (subject_id,))
    if cursor.fetchone():
        return subject_id

    # 创建学科
    cursor.execute(
        "INSERT OR IGNORE INTO subjects (id, name, phase) VALUES (?, ?, ?)",
        (subject_id, subject_name, "all"),
    )
    conn.commit()
    logger.debug(f"Created subject: {subject_id}")
    return subject_id


def create_book_from_node(node: dict) -> Book | None:
    """从节点创建书籍"""
    node_id = node.get("id", "")
    subject_id, grade, semester, publisher = parse_book_id(node_id)

    # 学科名称（从 properties 中获取）
    props = node.get("properties", {})
    subject_name = props.get("subject") or node.get("subject") or "数学"
    # 处理编码问题
    if not subject_name or subject_name.startswith("�"):
        subject_name = "数学"

    ensure_subject(subject_name)

    # 名称从 properties 或 node.name
    book_name = props.get("name") or node.get("name", "")
    if not book_name or book_name.startswith("�"):
        book_name = f"{subject_name}{grade}年级{semester}"

    return Book(
        id=node_id,
        subject_id=subject_id,
        grade=grade,
        semester=semester,
        publisher=publisher,
        version="2022",
        title=book_name,
    )


def create_section_from_node(node: dict) -> Section | None:
    """从节点创建章节"""
    node_id = node.get("id", "")
    node_type = infer_node_type(node_id, node)

    if node_type not in ("Chapter", "Section"):
        return None

    # 解析 book_id
    parts = node_id.split("_")
    if len(parts) >= 2:
        # 提取 book_id (去掉 _cptX 或 _secX 部分)
        if "_cpt" in node_id:
            book_id = node_id.split("_cpt")[0]
        elif "_sec" in node_id:
            book_id = node_id.split("_sec")[0]
        else:
            book_id = None
    else:
        book_id = None

    # 解析 parent_id
    parent_id = None
    if node_type == "Section":
        # 节的父节点是章
        if "_cpt" in node_id:
            chapter_num = node_id.split("_sec")[0].split("_cpt")[-1]
            parent_id = f"{node_id.split('_sec')[0]}_cpt{chapter_num}"

    # 解析 order_index
    order_index = 1
    if "_cpt" in node_id:
        match = re.search(r'_cpt(\d+)', node_id)
        if match:
            order_index = int(match.group(1))
    elif "_sec" in node_id:
        match = re.search(r'_sec(\d+)', node_id)
        if match:
            order_index = int(match.group(1))

    # depth: Chapter=0, Section=1
    depth = 0 if node_type == "Chapter" else 1

    return Section(
        id=node_id,
        book_id=book_id,
        parent_id=parent_id,
        title=clean_string(node.get("name", "")),
        depth=depth,
        order_index=order_index,
    )


def create_concept_from_node(node: dict) -> Concept | None:
    """从节点创建概念"""
    node_type = infer_node_type(node.get("id", ""), node)
    if node_type != "Concept":
        return None

    node_id = node.get("id", "")
    name = clean_string(node.get("name", ""))
    definition = clean_string(node.get("definition", ""))

    # 解析 importance
    importance = "掌握"
    if "importance" in node:
        importance = node["importance"]
    elif "level" in node:
        importance = node["level"]

    # 解析 aliases
    aliases = node.get("aliases", [])
    if not isinstance(aliases, list):
        aliases = [aliases] if aliases else []
    aliases = [clean_string(a) for a in aliases if clean_string(a)]

    # 解析 examples
    examples = node.get("examples", [])
    if not isinstance(examples, list):
        examples = [examples] if examples else []
    examples = [clean_string(e) for e in examples if clean_string(e)]

    # 摘要
    summary = clean_string(node.get("summary"))
    if not summary and definition:
        summary = definition[:200] + "..." if len(definition) > 200 else definition

    # 元数据
    metadata = {
        "source": "K12-KGraph",
        "formula": clean_string(node.get("formula")),
        "raw_id": node_id,
    }

    # 关联章节
    section_id = None
    if "section_id" in node:
        section_id = node["section_id"]
    elif "appears_in" in node:
        # 从 appears_in 关系推断
        appears = node["appears_in"]
        if isinstance(appears, list) and appears:
            section_id = appears[0].get("target_id") if isinstance(appears[0], dict) else appears[0]

    return Concept(
        id=node_id,
        name=name or node_id,
        section_id=section_id,
        definition=definition,
        importance=importance,
        formula=clean_string(node.get("formula")),
        aliases=aliases,
        examples=examples,
        summary=summary,
        metadata=metadata,
        created_by="import_kgraph.py",
    )


def create_skill_from_node(node: dict) -> Skill | None:
    """从节点创建技能"""
    node_type = infer_node_type(node.get("id", ""), node)
    if node_type != "Skill":
        return None

    node_id = node.get("id", "")

    # 关联的概念ID
    concept_id = node.get("concept_id")
    if not concept_id and "tests_concept" in node:
        # 从 tests_concept 关系获取
        tests = node["tests_concept"]
        if isinstance(tests, list) and tests:
            concept_id = tests[0].get("target_id") if isinstance(tests[0], dict) else tests[0]

    # 模板
    template = node.get("template", {})
    if isinstance(template, str):
        try:
            template = json.loads(template)
        except json.JSONDecodeError:
            template = {}

    return Skill(
        id=node_id,
        concept_id=concept_id,
        name=clean_string(node.get("name", "")),
        description=clean_string(node.get("description")),
        method=clean_string(node.get("method")),
        template=template,
        created_by="import_kgraph.py",
    )


def create_exercise_from_node(node: dict) -> Exercise | None:
    """从节点创建习题"""
    node_type = infer_node_type(node.get("id", ""), node)
    if node_type != "Exercise":
        return None

    node_id = node.get("id", "")
    props = node.get("properties", {})

    # 难度
    difficulty = props.get("difficulty") or node.get("difficulty", 3)
    if isinstance(difficulty, str):
        try:
            difficulty = int(difficulty)
        except ValueError:
            difficulty = 3
    difficulty = max(1, min(5, difficulty))

    # 类型
    exercise_type = props.get("type") or node.get("type") or "solve"
    if isinstance(exercise_type, list):
        exercise_type = exercise_type[0] if exercise_type else "solve"

    # 选项
    options = props.get("options") or node.get("options", [])
    if not isinstance(options, list):
        options = [options] if options else []

    # 题干、答案、解析（从 properties 优先）
    stem = clean_string(props.get("stem") or node.get("question") or node.get("stem", ""))
    answer = clean_string(props.get("answer") or node.get("answer", ""))
    analysis = clean_string(props.get("analysis") or node.get("analysis", ""))

    # 元数据
    metadata = {
        "source": "K12-KGraph",
        "raw_id": node_id,
        "chapter": props.get("chapter") or node.get("chapter"),
        "section": props.get("section") or node.get("section"),
    }

    return Exercise(
        id=node_id,
        stem=stem,
        answer=answer,
        analysis=analysis,
        difficulty=difficulty,
        type=exercise_type,
        options=options,
        source="K12-KGraph",
        metadata=metadata,
        created_by="import_kgraph.py",
    )


def import_nodes(nodes: list[dict], stats: dict) -> dict[str, Any]:
    """导入所有节点"""
    book_map = {}
    section_map = {}
    concept_map = {}
    skill_map = {}
    exercise_map = {}

    # 按类型分组
    books = []
    chapters_sections = []
    concepts = []
    skills = []
    exercises = []

    for node in nodes:
        node_type = infer_node_type(node.get("id", ""), node)
        if node_type == "Book":
            books.append(node)
        elif node_type in ("Chapter", "Section"):
            chapters_sections.append(node)
        elif node_type == "Concept":
            concepts.append(node)
        elif node_type == "Skill":
            skills.append(node)
        elif node_type == "Exercise":
            exercises.append(node)
        elif node_type == "Experiment":
            # 暂不支持实验
            stats["experiments"] = stats.get("experiments", 0) + 1

    # 导入书籍
    logger.info(f"Importing {len(books)} books...")
    for book_node in books:
        book = create_book_from_node(book_node)
        if book:
            book_map[book.id] = book_node
            try:
                BookCRUD.create(book)
                stats["books"] += 1
                logger.debug(f"Created book: {book.id}")
            except Exception as e:
                logger.debug(f"Book {book.id} may exist: {e}")

    # 导入章节
    logger.info(f"Importing {len(chapters_sections)} chapters/sections...")
    for section_node in chapters_sections:
        section = create_section_from_node(section_node)
        if section:
            section_map[section.id] = section.id
            try:
                db = get_db()
                conn = db.connect()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR IGNORE INTO sections
                       (id, book_id, parent_id, title, depth, order_index)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (section.id, section.book_id, section.parent_id,
                     section.title, section.depth, section.order_index),
                )
                conn.commit()
                stats["sections"] += 1
                logger.debug(f"Created section: {section.id}")
            except Exception as e:
                logger.debug(f"Section {section.id} may exist: {e}")

    # 导入概念
    logger.info(f"Importing {len(concepts)} concepts...")
    db = get_db()
    for concept_node in concepts:
        concept = create_concept_from_node(concept_node)
        if concept:
            concept_map[concept.id] = concept_node
            try:
                # 使用 INSERT OR IGNORE 避免重复错误
                conn = db.connect()
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute(
                    """INSERT OR IGNORE INTO concepts
                       (id, section_id, name, definition, importance, formula,
                        aliases, examples, summary, metadata, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (concept.id, concept.section_id, concept.name, concept.definition,
                     concept.importance, concept.formula,
                     json.dumps(concept.aliases, ensure_ascii=False),
                     json.dumps(concept.examples, ensure_ascii=False),
                     concept.summary,
                     json.dumps(concept.metadata, ensure_ascii=False),
                     concept.created_by),
                )
                if cursor.rowcount > 0:
                    stats["concepts"] += 1
                    logger.debug(f"Created concept: {concept.id}")
                conn.commit()
            except Exception as e:
                logger.debug(f"Concept {concept.id} error: {e}")

    # 导入技能
    logger.info(f"Importing {len(skills)} skills...")
    for skill_node in skills:
        skill = create_skill_from_node(skill_node)
        if skill:
            skill_map[skill.id] = skill_node
            try:
                conn = db.connect()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR IGNORE INTO skills
                       (id, concept_id, name, description, method, template, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (skill.id, skill.concept_id, skill.name, skill.description,
                     skill.method, json.dumps(skill.template, ensure_ascii=False),
                     skill.created_by),
                )
                if cursor.rowcount > 0:
                    stats["skills"] += 1
                    logger.debug(f"Created skill: {skill.id}")
                conn.commit()
            except Exception as e:
                logger.debug(f"Skill {skill.id} error: {e}")

    # 导入习题
    logger.info(f"Importing {len(exercises)} exercises...")
    for exercise_node in exercises:
        exercise = create_exercise_from_node(exercise_node)
        if exercise:
            exercise_map[exercise.id] = exercise_node
            try:
                ExerciseCRUD.create(exercise)
                stats["exercises"] += 1
                logger.debug(f"Created exercise: {exercise.id}")
            except Exception as e:
                logger.debug(f"Exercise {exercise.id} may exist: {e}")

    return {
        "book_map": book_map,
        "section_map": section_map,
        "concept_map": concept_map,
        "skill_map": skill_map,
        "exercise_map": exercise_map,
    }


def import_relations(edges: list[dict], maps: dict, stats: dict) -> None:
    """导入关系"""
    logger.info(f"Importing {len(edges)} relations...")

    for edge in edges:
        source_id = edge.get("source") or edge.get("source_id")
        target_id = edge.get("target") or edge.get("target_id")
        relation_type = edge.get("type") or edge.get("relation")

        if not source_id or not target_id or not relation_type:
            continue

        # 处理前置依赖
        if relation_type == "prerequisites_for":
            try:
                from src.knowledge.crud import Prerequisite
                prereq = Prerequisite(
                    source_id=source_id,
                    target_id=target_id,
                    strength=edge.get("strength", 1.0),
                    evidence=edge.get("properties", {}).get("evidence"),
                )
                PrerequisiteCRUD.add(prereq)
                stats["prerequisites"] += 1
                logger.debug(f"Added prerequisite: {source_id}->{target_id}")
            except Exception as e:
                logger.debug(f"Prerequisite {source_id}->{target_id}: {e}")

        # 处理习题-概念关联
        elif relation_type == "tests_concept":
            # tests_concept 使用 target_name_to_ids 格式
            targets = edge.get("target_name_to_ids", [])
            if not targets and "target" in edge:
                targets = [{"target": edge["target"]}]
            if not targets and "target_id" in edge:
                targets = [{"target": edge["target_id"]}]

            for target_info in targets:
                if isinstance(target_info, dict):
                    target_id = target_info.get("target") or target_info.get("target_id")
                else:
                    target_id = target_info

                if target_id:
                    try:
                        ExerciseConceptRelationCRUD.add(
                            exercise_id=source_id,
                            concept_id=target_id,
                            weight=edge.get("weight", 1.0),
                        )
                        stats["exercise_concepts"] += 1
                        logger.debug(f"Added exercise-concept: {source_id}->{target_id}")
                    except Exception as e:
                        logger.debug(f"Exercise-Concept {source_id}->{target_id}: {e}")

        # 处理关联关系
        elif relation_type == "relates_to":
            try:
                db = get_db()
                conn = db.connect()
                cursor = conn.cursor()
                # 为了防止重复，使用较小的ID
                cursor.execute(
                    """INSERT OR IGNORE INTO relation_related
                       (concept_a_id, concept_b_id, relation)
                       VALUES (?, ?, ?)""",
                    (source_id, target_id,
                     edge.get("properties", {}).get("relations", "相关")),
                )
                conn.commit()
                stats["related"] += 1
                logger.debug(f"Added related: {source_id}->{target_id}")
            except Exception as e:
                logger.debug(f"Related {source_id}->{target_id}: {e}")

        # 分类关系
        elif relation_type == "is_a":
            try:
                db = get_db()
                conn = db.connect()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR IGNORE INTO relation_is_a (child_id, parent_id)
                       VALUES (?, ?)""",
                    (source_id, target_id),
                )
                conn.commit()
                stats["is_a"] += 1
                logger.debug(f"Added is_a: {source_id}->{target_id}")
            except Exception as e:
                logger.debug(f"Is_a {source_id}->{target_id}: {e}")

        # 其他关系
        else:
            stats["other_relations"] = stats.get("other_relations", 0) + 1


def download_kgraph_files() -> list[Path]:
    """从 GitHub 下载 K12-KGraph 文件

    Returns:
        下载的文件路径列表
    """
    # GitHub raw 文件列表（示例数据，实际需要完整列表）
    files = [
        "demo/kg/math_7a_rjb.json",
        # 完整数据集需要更多文件，这里先使用示例
    ]

    base_url = "https://raw.githubusercontent.com/haolpku/K12-Dataset/main/"
    download_dir = Path("data/k12_kgraph")
    download_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []

    for file_path in files:
        url = base_url + file_path
        local_path = download_dir / Path(file_path).name

        logger.info(f"Downloading {file_path}...")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            local_path.write_bytes(response.content)
            downloaded.append(local_path)
            logger.info(f"Downloaded: {local_path}")
        except Exception as e:
            logger.warning(f"Failed to download {file_path}: {e}")

    return downloaded


def import_from_json(json_path: Path, stats: dict) -> None:
    """从 JSON 文件导入数据"""
    logger.info(f"Loading {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    logger.info(f"Found {len(nodes)} nodes, {len(edges)} edges")

    # 导入节点
    maps = import_nodes(nodes, stats)

    # 导入关系
    import_relations(edges, maps, stats)


def import_kgraph(
    json_path: str | None = None,
    force: bool = False,
) -> dict[str, int]:
    """导入 K12-KGraph 数据

    Args:
        json_path: JSON 文件路径，None 则从 GitHub 下载示例
        force: 是否强制重建

    Returns:
        导入统计
    """
    logger.info("Importing K12-KGraph dataset...")

    # 初始化数据库
    init_knowledge_db(force=force)

    stats = {
        "books": 0,
        "sections": 0,
        "concepts": 0,
        "skills": 0,
        "exercises": 0,
        "prerequisites": 0,
        "exercise_concepts": 0,
        "related": 0,
        "is_a": 0,
        "other_relations": 0,
    }

    if json_path:
        # 从指定文件导入
        import_from_json(Path(json_path), stats)
    else:
        # 从 GitHub 下载并导入
        files = download_kgraph_files()
        for file_path in files:
            import_from_json(file_path, stats)

    logger.info(f"Import completed: {stats}")
    return stats


def verify_import() -> dict[str, Any]:
    """验证导入结果"""
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()

    result = {}

    cursor.execute("SELECT COUNT(*) FROM books")
    result["books"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sections")
    result["sections"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM concepts")
    result["concepts"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM skills")
    result["skills"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM exercises")
    result["exercises"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relation_prerequisite")
    result["prerequisites"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relation_tests_concept")
    result["exercise_concepts"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relation_related")
    result["related"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relation_is_a")
    result["is_a"] = cursor.fetchone()[0]

    # 按学科统计
    cursor.execute("""
        SELECT b.subject_id, COUNT(*) as cnt
        FROM concepts c
        LEFT JOIN sections s ON c.section_id = s.id
        LEFT JOIN books b ON s.book_id = b.id
        GROUP BY b.subject_id
    """)
    result["by_subject"] = {row[0]: row[1] for row in cursor.fetchall()}

    return result


def main():
    """主函数"""
    import sys
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Import K12-KGraph dataset")
    parser.add_argument("--json", type=str, help="JSON file path")
    parser.add_argument("--force", action="store_true", help="Force rebuild database")
    parser.add_argument("--verify", action="store_true", help="Verify import only")

    args = parser.parse_args()

    if args.verify:
        result = verify_import()
        print("\n=== Import Verification ===")
        for key, value in result.items():
            if key != "by_subject":
                print(f"  {key}: {value}")
        print("\nBy Subject:")
        for subject, count in result.get("by_subject", {}).items():
            print(f"  {subject}: {count}")
        return

    try:
        stats = import_kgraph(json_path=args.json, force=args.force)
        print(f"\n=== Import Summary ===")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        result = verify_import()
        print(f"\n=== Database State ===")
        for key, value in result.items():
            if key != "by_subject":
                print(f"  {key}: {value}")

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()