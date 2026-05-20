# K12教育知识库框架设计文档
## Kid Agent 知识库架构方案 v1.0

---

## 一、研究背景与核心结论

### 1.1 现状

Kid Agent目前仅覆盖3-5年级数学30个知识点，存储在Python文件中。需要设计一个可扩展至12个年级x9+学科的知识库框架。

### 1.2 核心设计原则

- 从SQLite起步，架构上预留图数据库和向量库扩展能力
- Schema设计参考K12-KGraph（北大，2026）和清华EDUKG的成熟方案
- 检索采用"向量语义检索 + 知识图谱结构查询"混合方案（GraphRAG）
- 协作录入采用"API + 数据校验 + 审核流程"三层保障

---

## 二、中国K12教育体系学科覆盖方案

### 2.1 学科与年级分布

根据教育部2022年新课标，学科按年级分布如下：

```
小学阶段 (Grade 1-6):
  必修: 语文、数学
  3年级起: 英语、科学、信息科技
  贯通: 道德与法治、体育、音乐、美术

初中阶段 (Grade 7-9):
  必修: 语文、数学、英语、物理(8起)、化学(9起)、
        历史、地理、生物、道德与法治
  选修: 信息科技、体育、音乐、美术

高中阶段 (Grade 10-12):
  必修: 语文、数学、英语、物理、化学、生物、
        历史、地理、思想政治
  选修: 技术与设计、信息技术、体育、艺术
```

### 2.2 学科优先级

```
Phase 1 (当前): 数学 G3-G5
Phase 2 (6个月): 数学 G1-G12 全覆盖
Phase 3 (12个月): + 物理、化学
Phase 4 (18个月): + 语文、英语、生物、历史、地理、政治
```

---

## 三、知识库Schema设计

### 3.1 核心数据模型

参考K12-KGraph的7节点9边模型，结合Kid Agent需求：

```
层级结构:
学科 → 教材(Book) → 章(Chapter) → 节(Section) → 知识点(KnowledgePoint)

节点类型 (7种):
┌─────────────┬──────────────────────────────────────────────────┐
│ 节点类型     │ 核心属性                                         │
├─────────────┼──────────────────────────────────────────────────┤
│ Subject     │ id, name(语文/数学/...), code, phase(小学/初中/高中)│
│ Book        │ id, subject_id, grade, semester, publisher(人教版/..), version│
│ Chapter     │ id, book_id, title, order_index                   │
│ Section     │ id, chapter_id, title, order_index                │
│ Concept     │ id, name, definition, importance(了解/掌握/精通),   │
│             │ formula, aliases[], examples[], section_id          │
│ Skill       │ id, name, description, method, concept_id          │
│ Exercise    │ id, stem, answer, analysis, difficulty(1-5),       │
│             │ type(选择/填空/解答/应用), source                   │
└─────────────┴──────────────────────────────────────────────────┘

边/关系类型 (9种):
┌──────────────────────┬────────────────────────────────────┐
│ 关系类型              │ 含义                               │
├──────────────────────┼────────────────────────────────────┤
│ is_a                 │ 分类关系: 子概念 → 父概念            │
│ prerequisites_for    │ 前置依赖: 必须先学A才能学B          │
│ relates_to           │ 关联关系: 概念间的语义关联           │
│ tests_concept        │ 习题考查的知识点                     │
│ tests_skill          │ 习题考查的技能                       │
│ belongs_to           │ 概念/技能所属节                      │
│ is_part_of           │ 节属于章、章属于书                   │
│ common_mistake       │ 知识点的常见错误                     │
│ extension            │ 拓展知识（超纲但相关）               │
└──────────────────────┴────────────────────────────────────┘
```

### 3.2 SQLite DDL（Phase 1 实现）

```sql
-- 学科表
CREATE TABLE subjects (
    id          TEXT PRIMARY KEY,  -- 'math', 'chinese', 'physics'...
    name        TEXT NOT NULL,     -- '数学', '语文', '物理'...
    name_en     TEXT,
    phase       TEXT,              -- 'primary','middle','high','all'
    sort_order  INTEGER
);

-- 教材表
CREATE TABLE books (
    id          TEXT PRIMARY KEY,  -- 'math_3a_rjb' (数学三年级上人教版)
    subject_id  TEXT NOT NULL REFERENCES subjects(id),
    grade       INTEGER NOT NULL,  -- 1-12
    semester    TEXT NOT NULL,     -- '上', '下'
    publisher   TEXT DEFAULT '人教版',
    version     TEXT DEFAULT '2022',
    title       TEXT NOT NULL
);

-- 章节表（统一表达章和节的树形结构）
CREATE TABLE sections (
    id          TEXT PRIMARY KEY,  -- 'math_3a_ch01_s02'
    book_id     TEXT NOT NULL REFERENCES books(id),
    parent_id   TEXT REFERENCES sections(id),  -- NULL=章级, 非NULL=节级
    title       TEXT NOT NULL,
    depth       INTEGER NOT NULL,  -- 0=章, 1=节, 2=小节
    order_index INTEGER NOT NULL,
    UNIQUE(book_id, parent_id, order_index)
);

-- 知识点/概念表
CREATE TABLE concepts (
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
    created_by  TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version     INTEGER DEFAULT 1
);

-- 技能表
CREATE TABLE skills (
    id          TEXT PRIMARY KEY,
    concept_id  TEXT REFERENCES concepts(id),
    name        TEXT NOT NULL,
    description TEXT,
    method      TEXT,              -- 解题方法/步骤描述
    template    TEXT,              -- JSON: 解题模板
    created_by  TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version     INTEGER DEFAULT 1
);

-- 习题表
CREATE TABLE exercises (
    id          TEXT PRIMARY KEY,  -- UUID
    stem        TEXT NOT NULL,     -- 题目文本
    answer      TEXT NOT NULL,
    analysis    TEXT,              -- 解题过程
    difficulty  INTEGER CHECK(difficulty BETWEEN 1 AND 5),
    type        TEXT,              -- 'choice','fill','solve','apply'
    options     TEXT,              -- JSON: 选择题选项
    source      TEXT,              -- 来源：教材/教辅/教研
    metadata    TEXT,
    created_by  TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version     INTEGER DEFAULT 1
);

-- 常见错误表
CREATE TABLE common_mistakes (
    id          TEXT PRIMARY KEY,
    concept_id  TEXT REFERENCES concepts(id),
    mistake     TEXT NOT NULL,     -- 错误描述
    reason      TEXT,              -- 错因分析
    correction  TEXT,              -- 纠正方法
    frequency   INTEGER DEFAULT 0 -- 出现频率(0-100)
);

-- ========== 关系/边表（知识图谱的核心） ==========

-- 分类关系 (is_a)
CREATE TABLE relation_is_a (
    child_id    TEXT NOT NULL REFERENCES concepts(id),
    parent_id   TEXT NOT NULL REFERENCES concepts(id),
    PRIMARY KEY (child_id, parent_id)
);

-- 前置依赖关系 (prerequisites_for)
CREATE TABLE relation_prerequisite (
    source_id   TEXT NOT NULL,  -- 前置知识点id
    target_id   TEXT NOT NULL,  -- 目标知识点id
    source_type TEXT DEFAULT 'concept',  -- 'concept','skill'
    target_type TEXT DEFAULT 'concept',
    strength    REAL DEFAULT 1.0,  -- 依赖强度 0-1
    evidence    TEXT,              -- 依据描述
    PRIMARY KEY (source_id, target_id)
);

-- 关联关系 (relates_to)
CREATE TABLE relation_related (
    concept_a_id TEXT NOT NULL REFERENCES concepts(id),
    concept_b_id TEXT NOT NULL REFERENCES concepts(id),
    relation    TEXT,  -- 关系描述：如"对比","类比","推广"
    PRIMARY KEY (concept_a_id, concept_b_id)
);

-- 习题-知识点关联 (tests_concept)
CREATE TABLE relation_tests_concept (
    exercise_id TEXT NOT NULL REFERENCES exercises(id),
    concept_id  TEXT NOT NULL REFERENCES concepts(id),
    weight      REAL DEFAULT 1.0,  -- 该题考查此知识点的权重
    PRIMARY KEY (exercise_id, concept_id)
);

-- 习题-技能关联 (tests_skill)
CREATE TABLE relation_tests_skill (
    exercise_id TEXT NOT NULL REFERENCES exercises(id),
    skill_id    TEXT NOT NULL REFERENCES skills(id),
    PRIMARY KEY (exercise_id, skill_id)
);

-- 概念嵌入向量表（用于语义检索）
CREATE TABLE concept_embeddings (
    concept_id  TEXT PRIMARY KEY REFERENCES concepts(id),
    embedding   BLOB NOT NULL,     -- float32向量，二进制存储
    model_name  TEXT DEFAULT 'text2vec-base-chinese',
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 全文检索索引
CREATE VIRTUAL TABLE concepts_fts USING fts5(
    concept_id,
    name,
    definition,
    summary,
    aliases,
    content='concepts',
    content_rowid='rowid'
);

-- ========== 审核与协作表 ==========

-- 数据变更记录
CREATE TABLE change_log (
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

-- 索引
CREATE INDEX idx_concepts_section ON concepts(section_id);
CREATE INDEX idx_concepts_name ON concepts(name);
CREATE INDEX idx_exercises_type_diff ON exercises(type, difficulty);
CREATE INDEX idx_prereq_source ON relation_prerequisite(source_id);
CREATE INDEX idx_prereq_target ON relation_prerequisite(target_id);
CREATE INDEX idx_tests_concept ON relation_tests_concept(concept_id);
CREATE INDEX idx_change_log_status ON change_log(review_status);
```

### 3.3 ID命名规范

```
格式: {subject}_{grade}{semester}_{shortname}

示例:
  math_3a_frac_compare     → 数学3年级上_分数比较
  math_3a_frac_add         → 数学3年级上_分数加法
  physics_8b_ohm_law       → 物理8年级下_欧姆定律
  chem_9a_periodic_table   → 化学9年级上_元素周期表

章节:
  math_3a_ch01             → 数学3年级上 第1章
  math_3a_ch01_s01         → 数学3年级上 第1章第1节
```

---

## 四、存储引擎技术选型

### 4.1 三引擎分层设计

```
┌─────────────────────────────────────────────────────┐
│                  应用层 (FastAPI)                      │
├──────────────┬────────────────┬──────────────────────┤
│  结构化存储   │   图关系存储    │    向量语义存储        │
│  (SQLite)    │   (SQLite边表   │   (SQLite +          │
│              │    / Neo4j)     │    LanceDB嵌入)       │
├──────────────┼────────────────┼──────────────────────┤
│ 学科/教材/章 │  is_a          │  概念嵌入向量          │
│ 节/概念/习题 │  prerequisite  │  习题嵌入向量          │
│ 属性数据     │  relates_to    │  用于语义相似度检索    │
│ 全文检索FTS5 │  tests_*       │                      │
│ 事务/一致性  │  图遍历/路径   │                      │
└──────────────┴────────────────┴──────────────────────┘
```

### 4.2 各引擎选型理由

SQLite (结构化 + 图关系，Phase 1):
- 零部署，单文件，Python内置支持
- FTS5全文检索内置
- 边表模式可表达图关系，支持递归CTE做图遍历
- 迁移路径: 数据量增长后可迁移至PostgreSQL + Neo4j

LanceDB (向量存储，嵌入模式):
- 嵌入式，无需独立服务
- 原生Python支持
- 支持元数据过滤 + 向量检索混合查询
- 备选: ChromaDB（更简单但性能较弱）

---

## 五、检索方案设计（GraphRAG混合检索）

```
学生提问: "分数除法怎么做？"
         │
         ▼
    ┌─────────────┐
    │  意图解析    │  识别: 学科=数学, 概念=分数除法, 年级≈5
    └──────┬──────┘
           │
     ┌─────┴─────┐
     ▼            ▼
┌─────────┐  ┌──────────────┐
│ 向量检索 │  │ 图谱结构查询  │
│ Top-K   │  │ 定位核心节点  │
│ 语义相似 │  │ 前置依赖链   │
└────┬────┘  │ 关联概念     │
     │       └──────┬───────┘
     └──────┬───────┘
            ▼
    ┌───────────────┐
    │  结果融合排序  │
    │  知识点 + 习题 │
    │  + 前置知识链  │
    └───────┬───────┘
            ▼
    ┌───────────────┐
    │  LLM生成回答   │
    │  (带教学结构)  │
    └───────────────┘
```

---

## 六、众包协作录入框架

四层校验：
1. Schema校验（Pydantic自动）：字段类型、长度、格式
2. 业务规则校验：DAG环检测、去重、引用完整性
3. 内容质量校验：定义长度、答案必填、公式语法
4. 人工审核：change_log全程追溯，审核员approve/reject

---

## 七、参考的成熟教育平台与开源项目

1. K12-KGraph (北京大学, 2026) - 7节点9边Schema，6,579概念+1,364技能
   GitHub: github.com/haolpku/K12-Dataset
   HuggingFace: lhpku20010120/K12-KGraph

2. EDUKG (清华大学KEG, 2022) - 2.52亿实体+38.6亿三元组
   GitHub: github.com/THU-KEG/EDUKG

3. 松鼠AI - 数学单科>3万知识点（超细粒度）

4. 国家智慧教育平台 (smartedu.cn) - 教育部JY/T标准

---

## 八、实施路线图

```
Phase 1 (2-4周): 基础框架搭建
  □ 创建SQLite数据库，建表
  □ 实现核心CRUD API (FastAPI + Pydantic)
  □ 迁移现有30个知识点到新数据库
  □ 实现FTS5全文检索
  □ 实现基础向量检索

Phase 2 (1-2月): 知识图谱构建
  □ 建立数学G1-G12完整知识点树
  □ 建立前置依赖关系 (prerequisite)
  □ 实现递归图遍历查询
  □ 集成LanceDB向量库
  □ 实现混合检索 (向量 + FTS + 图)

Phase 3 (2-4月): 协作能力
  □ 实现审核工作流
  □ Excel/CSV批量导入工具
  □ LLM辅助知识点抽取流水线
  □ 知识图谱可视化界面

Phase 4 (4-6月): 多学科扩展
  □ 物理知识库构建
  □ 化学知识库构建
  □ 语文/英语知识库（不同schema适配）
  □ 跨学科知识关联
```

---

## 九、数据规模估算

```
9学科 ~120本书 → ~16,000概念
+ 技能: ~4,000
+ 习题: ~50,000 (每概念3-5题)
+ 关系边: ~80,000

存储: SQLite ~500MB, 向量 ~50MB, 全文索引 ~100MB
总计: ~700MB (SQLite完全够用)
```
