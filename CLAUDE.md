# CLAUDE.md — Kid Agent 项目指南

## 项目概述
少年助手（Kid Agent）— 小学3-5年级数学教学AI Agent

## 技术栈
- Python 3.12 + openai库（无框架，纯手写）
- SQLite（数据持久化）
- 智谱GLM / DeepSeek API
- Rich（CLI界面）

## 项目结构
```
src/
  agent/       — 核心Agent逻辑
    tutor.py   — TutorAgent 主教学循环（637行，最核心）
    planner.py — 学习路径规划
    roster.py  — 多学生管理
    session.py — 会话管理
    intent.py  — LLM意图识别
  engine/      — 四大引擎
    quiz.py    — 出题（LLM生成数学题）
    grader.py  — 判题（LLM评分+反馈）
    diagnose.py — 诊断（薄弱点分析）
    explain.py — 讲解（LLM讲解知识点）
    adaptive.py — 自适应难度（1-5级）
    review.py  — 艾宾浩斯复习调度
  knowledge/   — 知识体系
    math_g3g5.py — 30个知识点（3-5年级）
    graph.py   — 知识图谱（依赖关系）
  memory/      — 持久化
    store.py   — SQLite ORM（432行）
    student.py — 学生模型（掌握度/XP/等级）
  config/      — 配置
    settings.py — 配置加载+验证
  utils/       — 工具
    errors.py  — 自定义异常
    logger.py  — 日志系统
config/
  .env         — API密钥（GLM+DeepSeek）
  prompts/     — Prompt模板（tutor/quiz_gen/diagnose）
tests/         — 7个单元测试文件 + 1个集成测试
scripts/       — install.sh + start.sh
```

## 运行命令
```bash
cd ~/projects/kid-agent
source .venv/bin/activate
PYTHONPATH=. python3 -m src.main --mode cli --student NAME
```

## 测试
```bash
PYTHONPATH=. pytest tests/ -v           # 169个单元测试
PYTHONPATH=. python3 tests/integration.py # 集成测试（需要API）
```

## 核心接口
- TutorAgent.chat(student_id, message) → str  # 主对话入口
- TutorAgent.start_session(student_id) → str   # 开始会话

## 意图类型
quiz / answer / explain / diagnose / plan / report / chat

## 数据库表
students / quiz_history / mastery / review_schedule / student_records

## 关键设计决策
- 不用LangChain等框架，纯Python + openai库
- 30个知识点覆盖3-5年级所有数学模块
- 自适应难度5级 + 艾宾浩斯遗忘曲线
- XP经验值 + 等级系统 + 连续答对奖励
- 每个学生独立SQLite数据库文件

## API配置
GLM: https://open.bigmodel.cn/api/paas/v4
DeepSeek: https://api.deepseek.com
密钥在 config/.env
