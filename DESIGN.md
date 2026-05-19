# Kid Agent — 技术设计文档

> **版本：** v1.0  
> **日期：** 2026-05-20  
> **定位：** 少年助手 MVP（Phase 1 — 命令行版数学教学 Agent）

---

## 一、产品目标

做一个**能教小学3-5年级数学的AI教学Agent**，核心闭环：

```
诊断薄弱点 → 针对性出题 → 批改 → 讲解 → 再诊断
```

Phase 1 是命令行版，验证核心教学逻辑。后续加语音、Web界面、微信小程序。

---

## 二、技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 语言 | Python 3.10+ | Agent生态最成熟 |
| 后端框架 | FastAPI | 异步、轻量 |
| LLM | 智谱GLM / DeepSeek API | 国产便宜合规 |
| 数据库 | SQLite（MVP）→ PostgreSQL（生产） | 先轻后重 |
| 向量库 | ChromaDB（内嵌） | 知识点检索 |
| 语音STT | 智谱GLM语音API | Phase 2 |
| 语音TTS | Edge TTS / 智谱TTS | Phase 2 |
| 前端 | 命令行（Phase1）→ Web（Phase2）→ 小程序（Phase3） | 渐进式 |

---

## 三、项目结构

```
kid-agent/
├── DESIGN.md              # 本文件
├── README.md              # 项目说明
├── requirements.txt       # Python依赖
├── config/
│   ├── settings.py        # 配置管理（API keys等）
│   └── prompts/           # Prompt模板
│       ├── tutor.md       # 教学对话prompt
│       ├── quiz_gen.md    # 出题prompt
│       └── diagnose.md    # 诊断prompt
├── src/
│   ├── __init__.py
│   ├── main.py            # 入口（CLI / API server）
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── tutor.py       # 核心教学Agent逻辑
│   │   └── session.py     # 会话管理
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── quiz.py        # 出题引擎
│   │   ├── grader.py      # 批改引擎
│   │   ├── diagnose.py    # 诊断引擎（找薄弱点）
│   │   └── explain.py     # 讲解引擎（生成讲解内容）
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── graph.py       # 知识图谱（知识点+依赖关系）
│   │   └── math_g3g5.py   # 3-5年级数学知识点数据
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── student.py     # 学生模型（掌握状态、历史记录）
│   │   └── store.py       # 持久化存储（SQLite）
│   ├── voice/             # Phase 2
│   │   ├── __init__.py
│   │   ├── stt.py         # 语音转文字
│   │   └── tts.py         # 文字转语音
│   └── api/
│       ├── __init__.py
│       └── server.py      # FastAPI server（Phase 2）
├── data/
│   └── knowledge/         # 知识点JSON数据
├── tests/
│   ├── test_quiz.py
│   ├── test_grader.py
│   ├── test_diagnose.py
│   └── test_tutor.py
├── scripts/
│   └── seed_knowledge.py  # 导入知识点数据
└── docs/
    └── api.md             # API文档（Phase 2）
```

---

## 四、核心模块设计

### 4.1 知识图谱（knowledge/）

**数据结构：**

```python
# 知识点
class KnowledgePoint:
    id: str               # "math_g3_001"
    name: str             # "乘法口诀"
    grade: int            # 3
    subject: str          # "数学"
    difficulty: int       # 1-5
    prerequisites: list   # 前置知识点ID列表
    description: str      # 知识点描述
    examples: list        # 例题
    common_mistakes: list # 常见错误

# 学生掌握状态
class MasteryLevel:
    UNKNOWN = 0           # 未接触
    EXPOSING = 1          # 接触过
    FUZZY = 2             # 模糊（做题有对有错）
    MASTERED = 3          # 掌握（连续正确）
    FORGOTTEN = 4         # 遗忘（长时间没复习又错了）
```

**3-5年级核心知识点（初始数据）：**

三年级：
- 乘法口诀 / 一位数乘两位数 / 除法基础 / 分数初步 / 面积和周长

四年级：
- 多位数乘除 / 运算律 / 小数认识 / 角的度量 / 条形统计图

五年级：
- 小数四则运算 / 分数加减 / 方程初步 / 长方体正方体 / 折线统计图

### 4.2 教学引擎（engine/）

**出题引擎（quiz.py）：**

```python
class QuizEngine:
    def generate(self, knowledge_point: str, difficulty: int, 
                 student_history: list) -> Quiz:
        """根据知识点、难度、学生历史生成题目"""
        # 调用LLM生成题目，保证：
        # 1. 题目类型多样（选择/填空/应用题/口算）
        # 2. 难度匹配学生当前水平
        # 3. 避免出学生已经做对的同类型题
```

**批改引擎（grader.py）：**

```python
class GraderEngine:
    def grade(self, quiz: Quiz, student_answer: str) -> GradeResult:
        """批改学生答案"""
        # 返回：正确/错误、错误原因、提示语
        # 错误答案不直接给正确答案，先给提示引导
```

**诊断引擎（diagnose.py）：**

```python
class DiagnoseEngine:
    def diagnose(self, student_id: str) -> DiagnosisReport:
        """诊断学生薄弱点"""
        # 基于历史做题记录：
        # 1. 找出错率高的知识点
        # 2. 找出依赖链上的断点
        # 3. 生成学习建议（先补什么再补什么）
```

### 4.3 教学Agent（agent/tutor.py）

```python
class TutorAgent:
    """核心教学Agent - 协调所有引擎"""
    
    async def chat(self, student_id: str, message: str) -> str:
        """主对话入口"""
        # 1. 解析学生意图（闲聊/答题/提问/求助）
        # 2. 根据意图路由：
        #    - 答题 → grader.grade() → 反馈
        #    - 提问 → explain.explain() → 讲解
        #    - 闲聊 → 陪伴对话 + 引导学习
        #    - 求助 → diagnose → 推荐学习路径
        # 3. 更新学生记忆
    
    async def start_session(self, student_id: str) -> str:
        """开始一次学习会话"""
        # 1. 加载学生记忆
        # 2. 检查上次进度
        # 3. 决定今天学什么（薄弱点优先）
        # 4. 生成开场白（友好的，不是冷冰冰的）
    
    async def proactive_nudge(self, student_id: str) -> str:
        """主动推送（定时触发）"""
        # 1. 检查学生今天是否学习
        # 2. 生成鼓励性提醒
        # 3. 可以用游戏化语言（"你的连胜要断了哦"）
```

### 4.4 学生记忆（memory/）

```python
class StudentModel:
    id: str
    name: str
    grade: int
    mastery: dict         # {knowledge_point_id: MasteryLevel}
    history: list         # 做题历史
    preferences: dict     # 学习偏好（什么时间效率高、喜欢什么题型）
    streak_days: int      # 连续学习天数
    total_xp: int         # 经验值（游戏化）
```

---

## 五、LLM Prompt 设计原则

1. **角色设定：** "你是一个亲切、耐心的小学老师，叫小助手。你跟孩子说话用简单易懂的语言，多鼓励，少批评。"
2. **安全护栏：** 不回答与学习/成长无关的敏感话题；不给出有害内容
3. **教学逻辑：** 错误答案不直接纠正，先引导思考（"再想想？" "提示：先算括号里面的"）
4. **语气：** 儿童友好，像朋友不像老师，用emoji适度

---

## 六、Phase 1 开发计划（命令行版）

### Step 1：基础框架
- 项目初始化（requirements.txt, config）
- 知识点数据（3-5年级数学JSON）
- 学生记忆存储（SQLite）

### Step 2：核心引擎
- 出题引擎（调用LLM生成题目）
- 批改引擎（调用LLM批改+分析错误）
- 诊断引擎（基于历史数据分析薄弱点）

### Step 3：教学Agent
- 对话循环（CLI版）
- 会话管理
- 学习进度追踪

### Step 4：验证
- 用模拟学生数据测试完整教学闭环
- 单元测试覆盖核心模块

---

## 七、运行方式（Phase 1）

```bash
# 安装依赖
cd ~/projects/kid-agent
pip install -r requirements.txt

# 配置API Key
cp config/.env.example config/.env
# 编辑 config/.env 填入 GLM/DeepSeek API Key

# 启动命令行教学
python src/main.py --mode cli --student test_student_01

# 运行测试
pytest tests/
```

---

*DESIGN.md v1.0 · 2026-05-20*
