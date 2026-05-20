-- K12教育知识库Schema
-- Kid Agent 知识库架构 v1.0
-- 基于KNOWLEDGE-BASE-DESIGN.md设计

-- ========== 核心实体表 ==========

-- 学科表
CREATE TABLE IF NOT EXISTS subjects (
    id          TEXT PRIMARY KEY,  -- 'math', 'chinese', 'physics'...
    name        TEXT NOT NULL,     -- '数学', '语文', '物理'...
    name_en     TEXT,
    phase       TEXT,              -- 'primary','middle','high','all'
    sort_order  INTEGER DEFAULT 0
);

-- 教材表
CREATE TABLE IF NOT EXISTS books (
    id          TEXT PRIMARY KEY,  -- 'math_3a_rjb' (数学三年级上人教版)
    subject_id  TEXT NOT NULL REFERENCES subjects(id),
    grade       INTEGER NOT NULL,  -- 1-12
    semester    TEXT NOT NULL,     -- '上', '下'
    publisher   TEXT DEFAULT '人教版',
    version     TEXT DEFAULT '2022',
    title       TEXT NOT NULL
);

-- 章节表（统一表达章和节的树形结构）
CREATE TABLE IF NOT EXISTS sections (
    id          TEXT PRIMARY KEY,  -- 'math_3a_ch01_s02'
    book_id     TEXT NOT NULL REFERENCES books(id),
    parent_id   TEXT REFERENCES sections(id),  -- NULL=章级, 非NULL=节级
    title       TEXT NOT NULL,
    depth       INTEGER NOT NULL,  -- 0=章, 1=节, 2=小节
    order_index INTEGER NOT NULL,
    UNIQUE(book_id, parent_id, order_index)
);

-- 知识点/概念表
CREATE TABLE IF NOT EXISTS concepts (
    id          TEXT PRIMARY KEY,  -- 'math_3a_frac_compare'
    section_id  TEXT REFERENCES sections(id),
    name        TEXT NOT NULL,
    definition  TEXT,
    importance  TEXT DEFAULT '掌握',  -- '了解','理解','掌握','精通'
    formula     TEXT,              -- LaTeX公式
    aliases     TEXT,              -- JSON array: ["别名1","别名2"]
    examples    TEXT,              -- JSON array of example texts
    summary     TEXT,              -- 200字以内要点概述
    metadata    TEXT,              -- JSON: 扩展字段
    created_by  TEXT DEFAULT 'system',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version     INTEGER DEFAULT 1
);

-- 技能表
CREATE TABLE IF NOT EXISTS skills (
    id          TEXT PRIMARY KEY,
    concept_id  TEXT REFERENCES concepts(id),
    name        TEXT NOT NULL,
    description TEXT,
    method      TEXT,              -- 解题方法/步骤描述
    template    TEXT,              -- JSON: 解题模板
    created_by  TEXT DEFAULT 'system',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version     INTEGER DEFAULT 1
);

-- 习题表
CREATE TABLE IF NOT EXISTS exercises (
    id          TEXT PRIMARY KEY,  -- UUID
    stem        TEXT NOT NULL,     -- 题目文本
    answer      TEXT NOT NULL,
    analysis    TEXT,              -- 解题过程
    difficulty  INTEGER CHECK(difficulty BETWEEN 1 AND 5),
    type        TEXT,              -- 'choice','fill','solve','apply'
    options     TEXT,              -- JSON: 选择题选项
    source      TEXT,              -- 来源：教材/教辅/教研
    metadata    TEXT,
    created_by  TEXT DEFAULT 'system',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version     INTEGER DEFAULT 1
);

-- 常见错误表
CREATE TABLE IF NOT EXISTS common_mistakes (
    id          TEXT PRIMARY KEY,
    concept_id  TEXT REFERENCES concepts(id),
    mistake     TEXT NOT NULL,     -- 错误描述
    reason      TEXT,              -- 错因分析
    correction  TEXT,              -- 纠正方法
    frequency   INTEGER DEFAULT 0  -- 出现频率(0-100)
);

-- ========== 关系/边表（知识图谱的核心） ==========

-- 分类关系 (is_a)
CREATE TABLE IF NOT EXISTS relation_is_a (
    child_id    TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    parent_id   TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    PRIMARY KEY (child_id, parent_id)
);

-- 前置依赖关系 (prerequisites_for)
CREATE TABLE IF NOT EXISTS relation_prerequisite (
    source_id   TEXT NOT NULL,  -- 前置知识点id
    target_id   TEXT NOT NULL,  -- 目标知识点id
    source_type TEXT DEFAULT 'concept',  -- 'concept','skill'
    target_type TEXT DEFAULT 'concept',
    strength    REAL DEFAULT 1.0,  -- 依赖强度 0-1
    evidence    TEXT,              -- 依据描述
    PRIMARY KEY (source_id, target_id)
);

-- 关联关系 (relates_to)
CREATE TABLE IF NOT EXISTS relation_related (
    concept_a_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    concept_b_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    relation    TEXT,  -- 关系描述：如"对比","类比","推广"
    PRIMARY KEY (concept_a_id, concept_b_id)
);

-- 习题-知识点关联 (tests_concept)
CREATE TABLE IF NOT EXISTS relation_tests_concept (
    exercise_id TEXT NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    concept_id  TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    weight      REAL DEFAULT 1.0,  -- 该题考查此知识点的权重
    PRIMARY KEY (exercise_id, concept_id)
);

-- 习题-技能关联 (tests_skill)
CREATE TABLE IF NOT EXISTS relation_tests_skill (
    exercise_id TEXT NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    skill_id    TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, skill_id)
);

-- 概念嵌入向量表（用于语义检索）
CREATE TABLE IF NOT EXISTS concept_embeddings (
    concept_id  TEXT PRIMARY KEY REFERENCES concepts(id) ON DELETE CASCADE,
    embedding   BLOB NOT NULL,     -- float32向量，二进制存储
    model_name  TEXT DEFAULT 'text2vec-base-chinese',
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 全文检索索引
CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
    concept_id,
    name,
    definition,
    summary,
    content='concepts',
    content_rowid='rowid'
);

-- ========== 审核与协作表 ==========

-- 数据变更记录
CREATE TABLE IF NOT EXISTS change_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name  TEXT NOT NULL,
    record_id   TEXT NOT NULL,
    action      TEXT NOT NULL,     -- 'create','update','delete'
    old_data    TEXT,              -- JSON snapshot
    new_data    TEXT,              -- JSON snapshot
    changed_by  TEXT NOT NULL,
    changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_status TEXT DEFAULT 'pending',  -- 'pending','approved','rejected'
    reviewed_by TEXT,
    reviewed_at TIMESTAMP
);

-- ========== 索引 ==========

CREATE INDEX IF NOT EXISTS idx_concepts_section ON concepts(section_id);
CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(name);
CREATE INDEX IF NOT EXISTS idx_exercises_type_diff ON exercises(type, difficulty);
CREATE INDEX IF NOT EXISTS idx_prereq_source ON relation_prerequisite(source_id);
CREATE INDEX IF NOT EXISTS idx_prereq_target ON relation_prerequisite(target_id);
CREATE INDEX IF NOT EXISTS idx_tests_concept ON relation_tests_concept(concept_id);
CREATE INDEX IF NOT EXISTS idx_change_log_status ON change_log(review_status);
CREATE INDEX IF NOT EXISTS idx_books_subject_grade ON books(subject_id, grade);
CREATE INDEX IF NOT EXISTS idx_sections_book ON sections(book_id);