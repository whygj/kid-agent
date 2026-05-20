"""知识库 FastAPI REST API 端点

提供学科、教材、章节、知识点、技能、习题等的 CRUD 接口。
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from src.knowledge.crud import (
    ConceptCRUD, ExerciseCRUD, PrerequisiteCRUD, BookCRUD,
    Concept, Exercise, Prerequisite, generate_id,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# ========== 数据模型 ==========

class SubjectModel(BaseModel):
    """学科模型"""
    id: str
    name: str
    name_en: Optional[str] = None
    phase: Optional[str] = None
    sort_order: int = 0


class BookModel(BaseModel):
    """教材模型"""
    id: str
    subject_id: str
    grade: int
    semester: str
    publisher: str = "人教版"
    version: str = "2022"
    title: str = ""


class SectionModel(BaseModel):
    """章节模型"""
    id: str
    book_id: str
    parent_id: Optional[str] = None
    title: str
    depth: int
    order_index: int


class ConceptModel(BaseModel):
    """知识点模型"""
    id: str
    name: str
    section_id: Optional[str] = None
    definition: Optional[str] = None
    importance: str = "掌握"
    formula: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_by: str = "system"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: int = 1


class ConceptCreateRequest(BaseModel):
    """创建知识点请求"""
    name: str
    section_id: Optional[str] = None
    definition: Optional[str] = None
    importance: str = "掌握"
    formula: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("importance")
    @classmethod
    def validate_importance(cls, v):
        if v not in ["了解", "理解", "掌握", "精通"]:
            raise ValueError("importance 必须是：了解、理解、掌握、精通")
        return v


class ConceptUpdateRequest(BaseModel):
    """更新知识点请求"""
    name: Optional[str] = None
    definition: Optional[str] = None
    importance: Optional[str] = None
    formula: Optional[str] = None
    aliases: Optional[list[str]] = None
    examples: Optional[list[str]] = None
    summary: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class ExerciseModel(BaseModel):
    """习题模型"""
    id: str
    stem: str
    answer: str
    analysis: Optional[str] = None
    difficulty: int = 3
    type: str = "solve"
    options: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_by: str = "system"
    created_at: Optional[str] = None
    version: int = 1


class ExerciseCreateRequest(BaseModel):
    """创建习题请求"""
    stem: str
    answer: str
    analysis: Optional[str] = None
    difficulty: int = 3
    type: str = "solve"
    options: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v):
        if v < 1 or v > 5:
            raise ValueError("difficulty 必须在 1-5 之间")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v not in ["choice", "fill", "solve", "apply"]:
            raise ValueError("type 必须是：choice、fill、solve、apply")
        return v


class PrerequisiteModel(BaseModel):
    """前置依赖关系模型"""
    source_id: str
    target_id: str
    source_type: str = "concept"
    target_type: str = "concept"
    strength: float = 1.0
    evidence: Optional[str] = None


# ========== 响应模型 ==========

class ConceptResponse(ConceptModel):
    """知识点响应（包含前置依赖）"""
    prerequisites: list[str] = Field(default_factory=list)
    dependents: list[str] = Field(default_factory=list)


class ExerciseResponse(ExerciseModel):
    """习题响应（包含关联知识点）"""
    concepts: list[str] = Field(default_factory=list)


class DatabaseInfo(BaseModel):
    """数据库信息"""
    path: str
    size_mb: float
    subjects: int
    concepts: int
    exercises: int
    relations: int
    initialized: bool


# ========== API 端点 ==========

@router.get("/info", response_model=DatabaseInfo)
async def get_database_info():
    """获取知识库数据库信息"""
    from src.knowledge.db import get_db
    db = get_db()
    info = db.get_info()
    return DatabaseInfo(**info)


@router.get("/init")
async def initialize_database(force: bool = False):
    """初始化知识库数据库"""
    from src.knowledge.db import get_db
    db = get_db()
    if not force and db.is_initialized():
        return {"status": "already_initialized", "message": "数据库已初始化"}
    db.init_schema(force=force)
    return {"status": "initialized", "message": "数据库初始化完成"}


# ========== 学科和教材 ==========

@router.get("/subjects", response_model=list[SubjectModel])
async def list_subjects():
    """获取所有学科"""
    from src.knowledge.crud import SubjectCRUD
    subjects = SubjectCRUD.list_all()
    return [SubjectModel(**s.__dict__) for s in subjects]


@router.get("/books", response_model=list[BookModel])
async def list_books(
    subject_id: Optional[str] = Query(None, description="学科ID"),
    grade: Optional[int] = Query(None, description="年级"),
):
    """获取教材列表"""
    from src.knowledge.crud import BookCRUD
    if subject_id:
        books = BookCRUD.list_by_subject(subject_id)
    elif grade:
        # 暂时返回所有，可扩展按年级查询
        books = []
    else:
        books = []
    return [BookModel(**b.__dict__) for b in books]


# ========== 知识点 ==========

@router.get("/concepts", response_model=list[ConceptResponse])
async def list_concepts(
    section_id: Optional[str] = Query(None, description="章节ID"),
    grade: Optional[int] = Query(None, description="年级"),
    importance: Optional[str] = Query(None, description="重要性等级"),
    limit: int = Query(50, description="返回数量限制"),
):
    """获取知识点列表"""
    concepts = []

    if section_id:
        raw_concepts = ConceptCRUD.list_by_section(section_id)
        concepts.extend(raw_concepts)
    else:
        # 获取所有，限制数量
        from src.knowledge.db import get_db
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM concepts ORDER BY id LIMIT ?", (limit,))
        for row in cursor.fetchall():
            c = ConceptCRUD.get(row[0])
            if c:
                concepts.append(c)

    # 构建响应
    responses = []
    for c in concepts:
        prereqs = PrerequisiteCRUD.get_prerequisites(c.id)
        dependents = PrerequisiteCRUD.get_dependents(c.id)
        response = ConceptResponse(
            id=c.id,
            name=c.name,
            section_id=c.section_id,
            definition=c.definition,
            importance=c.importance,
            formula=c.formula,
            aliases=c.aliases,
            examples=c.examples,
            summary=c.summary,
            metadata=c.metadata,
            created_by=c.created_by,
            created_at=c.created_at.isoformat() if c.created_at else None,
            updated_at=c.updated_at.isoformat() if c.updated_at else None,
            version=c.version,
            prerequisites=prereqs,
            dependents=dependents,
        )
        responses.append(response)

    return responses


@router.get("/concepts/{concept_id}", response_model=ConceptResponse)
async def get_concept(concept_id: str):
    """获取单个知识点详情"""
    concept = ConceptCRUD.get(concept_id)
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"知识点 {concept_id} 不存在",
        )

    prereqs = PrerequisiteCRUD.get_prerequisites(concept_id)
    dependents = PrerequisiteCRUD.get_dependents(concept_id)

    return ConceptResponse(
        id=concept.id,
        name=concept.name,
        section_id=concept.section_id,
        definition=concept.definition,
        importance=concept.importance,
        formula=concept.formula,
        aliases=concept.aliases,
        examples=concept.examples,
        summary=concept.summary,
        metadata=concept.metadata,
        created_by=concept.created_by,
        created_at=concept.created_at.isoformat() if concept.created_at else None,
        updated_at=concept.updated_at.isoformat() if concept.updated_at else None,
        version=concept.version,
        prerequisites=prereqs,
        dependents=dependents,
    )


@router.post("/concepts", response_model=ConceptModel)
async def create_concept(request: ConceptCreateRequest):
    """创建知识点"""
    # 生成ID（如果需要可以自定义ID生成逻辑）
    concept_id = generate_id("concept")

    concept = Concept(
        id=concept_id,
        name=request.name,
        section_id=request.section_id,
        definition=request.definition,
        importance=request.importance,
        formula=request.formula,
        aliases=request.aliases,
        examples=request.examples,
        summary=request.summary,
        metadata=request.metadata,
    )

    created = ConceptCRUD.create(concept)
    return ConceptModel(**created.__dict__)


@router.put("/concepts/{concept_id}", response_model=ConceptModel)
async def update_concept(concept_id: str, request: ConceptUpdateRequest):
    """更新知识点"""
    # 构建更新字典
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.definition is not None:
        updates["definition"] = request.definition
    if request.importance is not None:
        updates["importance"] = request.importance
    if request.formula is not None:
        updates["formula"] = request.formula
    if request.aliases is not None:
        updates["aliases"] = request.aliases
    if request.examples is not None:
        updates["examples"] = request.examples
    if request.summary is not None:
        updates["summary"] = request.summary
    if request.metadata is not None:
        updates["metadata"] = request.metadata

    success = ConceptCRUD.update(concept_id, updates)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"知识点 {concept_id} 不存在或更新失败",
        )

    updated = ConceptCRUD.get(concept_id)
    return ConceptModel(**updated.__dict__)


@router.delete("/concepts/{concept_id}")
async def delete_concept(concept_id: str):
    """删除知识点"""
    success = ConceptCRUD.delete(concept_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"知识点 {concept_id} 不存在",
        )
    return {"status": "deleted", "id": concept_id}


@router.get("/concepts/{concept_id}/prerequisites", response_model=list[PrerequisiteModel])
async def get_concept_prerequisites(concept_id: str):
    """获取知识点的前置依赖"""
    # 作为前置的依赖
    prereq_ids = PrerequisiteCRUD.get_prerequisites(concept_id)

    # 作为后续的依赖
    from src.knowledge.crud import Prerequisite
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT source_id, strength FROM relation_prerequisite WHERE target_id = ?",
        (concept_id,)
    )
    result = []
    for row in cursor.fetchall():
        result.append(PrerequisiteModel(
            source_id=row[0],
            target_id=concept_id,
            strength=row[1],
        ))

    return result


@router.post("/concepts/{concept_id}/prerequisites")
async def add_prerequisite(concept_id: str, prereq: PrerequisiteModel):
    """添加前置依赖关系"""
    # 确保目标ID是当前概念
    prereq.target_id = concept_id
    created = PrerequisiteCRUD.add(prereq)
    return {"status": "created", **created.__dict__}


# ========== 习题 ==========

@router.get("/exercises", response_model=list[ExerciseResponse])
async def list_exercises(
    concept_id: Optional[str] = Query(None, description="关联的知识点ID"),
    difficulty: Optional[int] = Query(None, description="难度等级1-5"),
    type: Optional[str] = Query(None, description="题型"),
    limit: int = Query(20, description="返回数量限制"),
):
    """获取习题列表"""
    exercises = []

    if concept_id:
        # 获取关联该知识点的习题
        from src.knowledge.crud import ExerciseConceptRelationCRUD
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT exercise_id FROM relation_tests_concept
               WHERE concept_id = ?""",
            (concept_id,)
        )
        for row in cursor.fetchall():
            e = ExerciseCRUD.get(row[0])
            if e:
                exercises.append(e)
    else:
        # 根据条件筛选
        if difficulty:
            exercises = ExerciseCRUD.random_by_difficulty(difficulty, limit)

    # 构建响应
    responses = []
    for e in exercises[:limit]:
        # 获取关联的知识点
        db = get_db()
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT concept_id FROM relation_tests_concept
               WHERE exercise_id = ?""",
            (e.id,)
        )
        concepts = [row[0] for row in cursor.fetchall()]

        response = ExerciseResponse(
            id=e.id,
            stem=e.stem,
            answer=e.answer,
            analysis=e.analysis,
            difficulty=e.difficulty,
            type=e.type,
            options=e.options,
            source=e.source,
            metadata=e.metadata,
            created_by=e.created_by,
            created_at=e.created_at.isoformat() if e.created_at else None,
            version=e.version,
            concepts=concepts,
        )
        responses.append(response)

    return responses


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: str):
    """获取单个习题详情"""
    exercise = ExerciseCRUD.get(exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"习题 {exercise_id} 不存在",
        )

    # 获取关联的知识点
    db = get_db()
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT concept_id FROM relation_tests_concept
           WHERE exercise_id = ?""",
        (exercise_id,)
    )
    concepts = [row[0] for row in cursor.fetchall()]

    return ExerciseResponse(
        id=exercise.id,
        stem=exercise.stem,
        answer=exercise.answer,
        analysis=exercise.analysis,
        difficulty=exercise.difficulty,
        type=exercise.type,
        options=exercise.options,
        source=exercise.source,
        metadata=exercise.metadata,
        created_by=exercise.created_by,
        created_at=exercise.created_at.isoformat() if exercise.created_at else None,
        version=exercise.version,
        concepts=concepts,
    )


@router.post("/exercises", response_model=ExerciseModel)
async def create_exercise(request: ExerciseCreateRequest):
    """创建习题"""
    exercise_id = generate_id("exercise")

    exercise = Exercise(
        id=exercise_id,
        stem=request.stem,
        answer=request.answer,
        analysis=request.analysis,
        difficulty=request.difficulty,
        type=request.type,
        options=request.options,
        source=request.source,
        metadata=request.metadata,
    )

    created = ExerciseCRUD.create(exercise)
    return ExerciseModel(**created.__dict__)


# ========== 搜索 ==========

@router.get("/search")
async def search_concepts(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, description="返回数量限制"),
):
    """全文搜索知识点"""
    concepts = ConceptCRUD.search(query, limit)
    return [ConceptModel(**c.__dict__) for c in concepts]


# ========== 导入 ==========

@router.post("/import/migrate-seed")
async def migrate_seed_data(force: bool = False):
    """迁移30个旧知识点到新数据库"""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "src.knowledge.migrate_seed"] + (["--force"] if force else []),
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"迁移失败: {result.stderr}",
        )

    return {"status": "success", "output": result.stdout}


@router.post("/import/grade")
async def import_grade_points(
    grade: int = Query(..., description="年级 (1-9)"),
    force: bool = False,
):
    """导入指定年级的知识点到数据库"""
    import subprocess
    import sys
    from pathlib import Path

    # 检查知识点文件
    grade_files = {
        1: "math_g1g2.py",
        2: "math_g1g2.py",
        3: "math_g3g5_v2.py",
        4: "math_g3g5_v2.py",
        5: "math_g3g5_v2.py",
        6: "math_g6.py",
        7: "math_g7.py",
        8: "math_g8g9.py",
        9: "math_g8g9.py",
    }

    file_name = grade_files.get(grade)
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持年级 {grade}",
        )

    file_path = Path(__file__).parent / file_name
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"知识点文件 {file_name} 不存在",
        )

    # 这里需要实现导入逻辑
    # 暂时返回提示
    return {
        "status": "pending",
        "message": f"请使用 import_points.py 脚本导入 {file_name}",
        "file": str(file_path),
    }