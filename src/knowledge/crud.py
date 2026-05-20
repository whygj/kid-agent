"""知识库CRUD操作模块

提供对知识库数据库的增删改查操作。
"""

import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional

from src.knowledge.db import get_db

logger = logging.getLogger(__name__)


@dataclass
class Subject:
    """学科数据类"""
    id: str
    name: str
    name_en: str | None = None
    phase: str | None = None
    sort_order: int = 0


@dataclass
class Book:
    """教材数据类"""
    id: str
    subject_id: str
    grade: int
    semester: str
    publisher: str = "人教版"
    version: str = "2022"
    title: str = ""


@dataclass
class Section:
    """章节/节数据类"""
    id: str
    book_id: str
    parent_id: str | None
    title: str
    depth: int
    order_index: int


@dataclass
class Concept:
    """知识点/概念数据类"""
    id: str
    name: str
    section_id: str | None = None
    definition: str | None = None
    importance: str = "掌握"
    formula: str | None = None
    aliases: list[str] | None = None
    examples: list[str] | None = None
    summary: str | None = None
    metadata: dict[str, Any] | None = None
    created_by: str = "system"
    created_at: str | None = None
    updated_at: str | None = None
    version: int = 1

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.examples is None:
            self.examples = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Skill:
    """技能数据类"""
    id: str
    concept_id: str | None = None
    name: str = ""
    description: str | None = None
    method: str | None = None
    template: dict[str, Any] | None = None
    created_by: str = "system"
    created_at: str | None = None
    version: int = 1

    def __post_init__(self):
        if self.template is None:
            self.template = {}


@dataclass
class Exercise:
    """习题数据类"""
    id: str
    stem: str
    answer: str
    analysis: str | None = None
    difficulty: int = 3
    type: str = "solve"
    options: list[str] | None = None
    source: str | None = None
    metadata: dict[str, Any] | None = None
    created_by: str = "system"
    created_at: str | None = None
    version: int = 1

    def __post_init__(self):
        if self.options is None:
            self.options = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CommonMistake:
    """常见错误数据类"""
    id: str
    concept_id: str | None = None
    mistake: str = ""
    reason: str | None = None
    correction: str | None = None
    frequency: int = 0


@dataclass
class Prerequisite:
    """前置依赖关系数据类"""
    source_id: str
    target_id: str
    source_type: str = "concept"
    target_type: str = "concept"
    strength: float = 1.0
    evidence: str | None = None


class SubjectCRUD:
    """学科CRUD操作"""

    @staticmethod
    def create(subject: Subject) -> Subject:
        """创建学科"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO subjects (id, name, name_en, phase, sort_order)
               VALUES (?, ?, ?, ?, ?)""",
            (subject.id, subject.name, subject.name_en, subject.phase, subject.sort_order),
        )
        conn.commit()
        logger.debug(f"Created subject: {subject.id}")
        return subject

    @staticmethod
    def get(subject_id: str) -> Optional[Subject]:
        """获取学科"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        row = cursor.fetchone()
        if row:
            return Subject(**dict(row))
        return None

    @staticmethod
    def list_all() -> list[Subject]:
        """获取所有学科"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM subjects ORDER BY sort_order")
        return [Subject(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def delete(subject_id: str) -> bool:
        """删除学科"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug(f"Deleted subject: {subject_id}")
        return deleted


class BookCRUD:
    """教材CRUD操作"""

    @staticmethod
    def create(book: Book) -> Book:
        """创建教材"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO books (id, subject_id, grade, semester, publisher, version, title)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (book.id, book.subject_id, book.grade, book.semester,
             book.publisher, book.version, book.title),
        )
        conn.commit()
        logger.debug(f"Created book: {book.id}")
        return book

    @staticmethod
    def get(book_id: str) -> Optional[Book]:
        """获取教材"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        if row:
            return Book(**dict(row))
        return None

    @staticmethod
    def list_by_subject(subject_id: str) -> list[Book]:
        """按学科获取教材列表"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM books WHERE subject_id = ? ORDER BY grade, semester",
            (subject_id,)
        )
        return [Book(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def get_by_grade(subject_id: str, grade: int, semester: str) -> Optional[Book]:
        """按年级和学期获取教材"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM books WHERE subject_id = ? AND grade = ? AND semester = ?",
            (subject_id, grade, semester)
        )
        row = cursor.fetchone()
        if row:
            return Book(**dict(row))
        return None


class ConceptCRUD:
    """知识点/概念CRUD操作"""

    @staticmethod
    def create(concept: Concept) -> Concept:
        """创建知识点"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute(
            """INSERT INTO concepts
               (id, section_id, name, definition, importance, formula, aliases, examples, summary, metadata, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (concept.id, concept.section_id, concept.name, concept.definition,
             concept.importance, concept.formula,
             json.dumps(concept.aliases, ensure_ascii=False),
             json.dumps(concept.examples, ensure_ascii=False),
             concept.summary,
             json.dumps(concept.metadata, ensure_ascii=False),
             concept.created_by),
        )
        conn.commit()
        logger.debug(f"Created concept: {concept.id}")
        return concept

    @staticmethod
    def get(concept_id: str) -> Optional[Concept]:
        """获取知识点"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            # 解析JSON字段
            data["aliases"] = json.loads(data["aliases"]) if data["aliases"] else []
            data["examples"] = json.loads(data["examples"]) if data["examples"] else []
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
            return Concept(**data)
        return None

    @staticmethod
    def update(concept_id: str, updates: dict[str, Any]) -> bool:
        """更新知识点"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        valid_fields = {"name", "definition", "importance", "formula", "summary"}
        json_fields = {"aliases", "examples", "metadata"}

        set_clauses = []
        values = []

        for field, value in updates.items():
            if field not in valid_fields and field not in json_fields:
                continue
            if field in json_fields:
                set_clauses.append(f"{field} = ?")
                values.append(json.dumps(value, ensure_ascii=False))
            else:
                set_clauses.append(f"{field} = ?")
                values.append(value)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(concept_id)

        sql = f"UPDATE concepts SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        updated = cursor.rowcount > 0
        if updated:
            logger.debug(f"Updated concept: {concept_id}")
        return updated

    @staticmethod
    def delete(concept_id: str) -> bool:
        """删除知识点"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug(f"Deleted concept: {concept_id}")
        return deleted

    @staticmethod
    def list_by_section(section_id: str) -> list[Concept]:
        """按章节获取知识点列表"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM concepts WHERE section_id = ?", (section_id,))
        concepts = []
        for row in cursor.fetchall():
            data = dict(row)
            data["aliases"] = json.loads(data["aliases"]) if data["aliases"] else []
            data["examples"] = json.loads(data["examples"]) if data["examples"] else []
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
            concepts.append(Concept(**data))
        return concepts

    @staticmethod
    def search(query: str, limit: int = 20) -> list[Concept]:
        """全文检索知识点"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT c.* FROM concepts c
               JOIN concepts_fts f ON c.rowid = f.rowid
               WHERE concepts_fts MATCH ?
               ORDER BY c.importance DESC
               LIMIT ?""",
            (query, limit)
        )
        concepts = []
        for row in cursor.fetchall():
            data = dict(row)
            data["aliases"] = json.loads(data["aliases"]) if data["aliases"] else []
            data["examples"] = json.loads(data["examples"]) if data["examples"] else []
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
            concepts.append(Concept(**data))
        return concepts


class SkillCRUD:
    """技能CRUD操作"""

    @staticmethod
    def create(skill: Skill) -> Skill:
        """创建技能"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO skills (id, concept_id, name, description, method, template, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (skill.id, skill.concept_id, skill.name, skill.description,
             skill.method, json.dumps(skill.template, ensure_ascii=False), skill.created_by),
        )
        conn.commit()
        logger.debug(f"Created skill: {skill.id}")
        return skill

    @staticmethod
    def get(skill_id: str) -> Optional[Skill]:
        """获取技能"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["template"] = json.loads(data["template"]) if data["template"] else {}
            return Skill(**data)
        return None

    @staticmethod
    def list_by_concept(concept_id: str) -> list[Skill]:
        """按知识点获取技能列表"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM skills WHERE concept_id = ?", (concept_id,))
        skills = []
        for row in cursor.fetchall():
            data = dict(row)
            data["template"] = json.loads(data["template"]) if data["template"] else {}
            skills.append(Skill(**data))
        return skills


class ExerciseCRUD:
    """习题CRUD操作"""

    @staticmethod
    def create(exercise: Exercise) -> Exercise:
        """创建习题"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO exercises
               (id, stem, answer, analysis, difficulty, type, options, source, metadata, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (exercise.id, exercise.stem, exercise.answer, exercise.analysis,
             exercise.difficulty, exercise.type,
             json.dumps(exercise.options, ensure_ascii=False),
             exercise.source, json.dumps(exercise.metadata, ensure_ascii=False),
             exercise.created_by),
        )
        conn.commit()
        logger.debug(f"Created exercise: {exercise.id}")
        return exercise

    @staticmethod
    def get(exercise_id: str) -> Optional[Exercise]:
        """获取习题"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data["options"] = json.loads(data["options"]) if data["options"] else []
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
            return Exercise(**data)
        return None

    @staticmethod
    def list_by_concept(concept_id: str, limit: int = 10) -> list[Exercise]:
        """按知识点获取习题列表"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT e.* FROM exercises e
               JOIN relation_tests_concept r ON e.id = r.exercise_id
               WHERE r.concept_id = ?
               ORDER BY e.difficulty
               LIMIT ?""",
            (concept_id, limit)
        )
        exercises = []
        for row in cursor.fetchall():
            data = dict(row)
            data["options"] = json.loads(data["options"]) if data["options"] else []
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
            exercises.append(Exercise(**data))
        return exercises

    @staticmethod
    def random_by_difficulty(difficulty: int, count: int = 1) -> list[Exercise]:
        """随机获取指定难度的习题"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM exercises WHERE difficulty = ? ORDER BY RANDOM() LIMIT ?",
            (difficulty, count)
        )
        exercises = []
        for row in cursor.fetchall():
            data = dict(row)
            data["options"] = json.loads(data["options"]) if data["options"] else []
            data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
            exercises.append(Exercise(**data))
        return exercises


class CommonMistakeCRUD:
    """常见错误CRUD操作"""

    @staticmethod
    def create(mistake: CommonMistake) -> CommonMistake:
        """创建常见错误"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO common_mistakes (id, concept_id, mistake, reason, correction, frequency)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (mistake.id, mistake.concept_id, mistake.mistake,
             mistake.reason, mistake.correction, mistake.frequency),
        )
        conn.commit()
        logger.debug(f"Created common_mistake: {mistake.id}")
        return mistake

    @staticmethod
    def list_by_concept(concept_id: str) -> list[CommonMistake]:
        """按知识点获取常见错误列表"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM common_mistakes WHERE concept_id = ? ORDER BY frequency DESC",
            (concept_id,)
        )
        return [CommonMistake(**dict(row)) for row in cursor.fetchall()]


class PrerequisiteCRUD:
    """前置依赖关系CRUD操作"""

    @staticmethod
    def add(prereq: Prerequisite) -> Prerequisite:
        """添加前置依赖关系"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT OR REPLACE INTO relation_prerequisite
               (source_id, target_id, source_type, target_type, strength, evidence)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (prereq.source_id, prereq.target_id, prereq.source_type,
             prereq.target_type, prereq.strength, prereq.evidence),
        )
        conn.commit()
        logger.debug(f"Added prerequisite: {prereq.source_id} -> {prereq.target_id}")
        return prereq

    @staticmethod
    def get_prerequisites(target_id: str) -> list[str]:
        """获取知识点的前置依赖ID列表"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT source_id FROM relation_prerequisite WHERE target_id = ? ORDER BY strength DESC",
            (target_id,)
        )
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def get_dependents(source_id: str) -> list[str]:
        """获取依赖该知识点的后续知识点ID列表"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT target_id FROM relation_prerequisite WHERE source_id = ? ORDER BY strength DESC",
            (source_id,)
        )
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def delete(source_id: str, target_id: str) -> bool:
        """删除前置依赖关系"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM relation_prerequisite WHERE source_id = ? AND target_id = ?",
            (source_id, target_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug(f"Deleted prerequisite: {source_id} -> {target_id}")
        return deleted


class ExerciseConceptRelationCRUD:
    """习题-知识点关联CRUD操作"""

    @staticmethod
    def add(exercise_id: str, concept_id: str, weight: float = 1.0) -> None:
        """添加习题-知识点关联"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT OR REPLACE INTO relation_tests_concept (exercise_id, concept_id, weight)
               VALUES (?, ?, ?)""",
            (exercise_id, concept_id, weight)
        )
        conn.commit()
        logger.debug(f"Added relation: exercise {exercise_id} -> concept {concept_id}")

    @staticmethod
    def delete(exercise_id: str, concept_id: str) -> bool:
        """删除习题-知识点关联"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM relation_tests_concept WHERE exercise_id = ? AND concept_id = ?",
            (exercise_id, concept_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug(f"Deleted relation: exercise {exercise_id} -> concept {concept_id}")
        return deleted


class ChangeLogCRUD:
    """变更日志CRUD操作"""

    @staticmethod
    def log_change(
        table_name: str,
        record_id: str,
        action: str,
        old_data: dict | None = None,
        new_data: dict | None = None,
        changed_by: str = "system"
    ) -> int:
        """记录数据变更

        Returns:
            int: 变更记录ID
        """
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO change_log
               (table_name, record_id, action, old_data, new_data, changed_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (table_name, record_id, action,
             json.dumps(old_data, ensure_ascii=False) if old_data else None,
             json.dumps(new_data, ensure_ascii=False) if new_data else None,
             changed_by)
        )
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def list_pending() -> list[dict[str, Any]]:
        """获取待审核的变更记录"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT * FROM change_log
               WHERE review_status = 'pending'
               ORDER BY changed_at DESC"""
        )
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def approve(log_id: int, reviewed_by: str) -> bool:
        """审核通过变更记录"""
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute(
            """UPDATE change_log
               SET review_status = 'approved', reviewed_by = ?, reviewed_at = ?
               WHERE id = ?""",
            (reviewed_by, datetime.now().isoformat(), log_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def generate_id(prefix: str) -> str:
    """生成唯一ID

    Args:
        prefix: ID前缀（如 'concept', 'exercise'）

    Returns:
        str: 唯一ID
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}"