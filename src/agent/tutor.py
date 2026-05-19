"""核心教学Agent - 协调所有引擎进行教学对话"""

import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from src.agent.session import Session, SessionManager, SessionState
from src.config.settings import get_config
from src.engine.diagnose import get_diagnose_engine
from src.engine.explain import get_explain_engine, Explanation
from src.engine.grader import get_grader_engine, GradeResult
from src.engine.quiz import get_quiz_engine, Quiz
from src.knowledge.graph import KnowledgeGraph, get_graph
from src.knowledge.math_g3g5 import get_points_by_grade
from src.memory.store import get_store, QuizHistoryORM
from src.memory.student import StudentModel


class TutorAgent:
    """核心教学Agent"""

    def __init__(self):
        """初始化教学Agent"""
        self.config = get_config()
        self.client: AsyncOpenAI | None = None
        self.session_manager = SessionManager()
        self._graph = get_graph()
        self._system_prompt = self._load_system_prompt()

        # 引擎（懒加载）
        self._quiz_engine = None
        self._grader_engine = None
        self._explain_engine = None
        self._diagnose_engine = None
        self._store = None

    def _load_system_prompt(self) -> str:
        """加载系统prompt"""
        prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "tutor.md"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return """你是小助手，一个亲切、耐心的小学数学老师。

你的特点：
1. 用简单易懂的语言，像朋友一样和孩子交流
2. 多鼓励、少批评，用emoji增加趣味性
3. 循序渐进引导思考，不直接给答案
4. 关心孩子的学习状态和情绪

你的工作：
1. 出题：根据孩子的情况出合适的题
2. 批改：温柔地批改，错误时给提示
3. 讲解：孩子不懂就耐心讲解
4. 鼓励：经常夸奖孩子的进步

请用温柔亲切的语气回答，多用emoji！"""

    async def _get_engines(self):
        """获取所有引擎"""
        if self._quiz_engine is None:
            self._quiz_engine = await get_quiz_engine()
        if self._grader_engine is None:
            self._grader_engine = await get_grader_engine()
        if self._explain_engine is None:
            self._explain_engine = await get_explain_engine()
        if self._diagnose_engine is None:
            self._diagnose_engine = await get_diagnose_engine()
        if self._store is None:
            self._store = await get_store()
        if self.client is None:
            self.client = self.config.get_client(async_client=True)

    async def start_session(self, student_id: str) -> str:
        """开始学习会话"""
        await self._get_engines()

        # 获取或创建学生
        student = await self._store.get_student(student_id)
        if not student:
            student = await self._store.create_student(student_id, "同学", 3)

        # 创建会话
        session = self.session_manager.create_session(student_id)

        # 生成开场白
        greeting = await self._generate_greeting(student)

        session.add_message("assistant", greeting, "command")
        session.set_state(SessionState.QUIZ)

        return greeting

    async def _generate_greeting(self, student) -> str:
        """生成开场白"""
        # 获取历史统计
        stats = await self._store.get_student_history(student.id, limit=5)

        if not stats:
            return """👋 你好呀！我是小助手，今天我们一起学数学吧！

我们先来做个小测试，看看你最近学了哪些内容，好不好？

准备好了就告诉我"开始"哦~"""

        recent_count = len(stats)
        correct_count = sum(1 for r in stats if r.is_correct)
        accuracy = correct_count / recent_count if recent_count > 0 else 0

        if accuracy >= 0.8:
            emoji = "🌟"
            comment = "进步很大！"
        elif accuracy >= 0.6:
            emoji = "💪"
            comment = "继续保持！"
        else:
            emoji = "📚"
            comment = "加油加油！"

        return f"""👋 欢迎回来！{emoji}

你最近完成了{recent_count}道题，正确率{accuracy:.0%}，{comment}

今天你想学什么？可以告诉我：
- "出题" - 我给你出题做
- "帮我看看" - 我帮你分析学习情况
- 或者直接问任何数学问题！

让我们开始吧~ ✨"""

    async def chat(self, student_id: str, message: str) -> str:
        """主对话入口"""
        await self._get_engines()

        session = self.session_manager.get_session(student_id)
        if not session:
            session = await self.start_session(student_id)

        session.add_message("user", message, "chat")

        # 解析意图
        intent = await self._parse_intent(message, session)

        # 根据意图路由
        if intent == "quiz":
            response = await self._handle_quiz(student_id, session)
        elif intent == "answer":
            response = await self._handle_answer(student_id, message, session)
        elif intent == "explain":
            response = await self._handle_explain(student_id, message, session)
        elif intent == "diagnose":
            response = await self._handle_diagnose(student_id, session)
        elif intent == "chat":
            response = await self._handle_chat(student_id, message, session)
        else:
            response = await self._handle_chat(student_id, message, session)

        session.add_message("assistant", response, intent)
        return response

    async def _parse_intent(self, message: str, session: Session) -> str:
        """解析用户意图"""
        message_lower = message.strip().lower()

        # 简单规则
        keywords = {
            "quiz": ["出题", "题目", "做道题", "开始", "next", "下一题"],
            "answer": ["答案", "答", "答案是"],
            "explain": ["讲解", "解释", "为什么", "不懂", "教我"],
            "diagnose": ["诊断", "分析", "看看", "情况", "复习"],
        }

        for intent, words in keywords.items():
            if any(word in message_lower for word in words):
                return intent

        # 如果在做题状态，可能是在回答
        if session.state == SessionState.QUIZ and session.current_quiz:
            # 简单的答案检测
            if message.replace(" ", "").replace("，", "").replace("。", ""):
                return "answer"

        return "chat"

    async def _handle_quiz(self, student_id: str, session: Session) -> str:
        """处理出题请求"""
        # 获取学生信息
        student = await self._store.get_student(student_id)
        grade = student.grade if student else 3

        # 获取年级知识点
        points = get_points_by_grade(grade)
        if not points:
            return "哎呀，还没有加载知识点呢~ 先休息一下吧 😴"

        # 简单选择知识点（可以改进为根据薄弱点）
        point = points[len(session.messages) % len(points)]

        # 生成题目
        quiz = await self._quiz_engine.generate(point)

        # 保存当前题目
        session.current_quiz = quiz
        session.set_state(SessionState.QUIZ)

        return f"""📝 来做道题吧！

**{point.name}**

{quiz.question}

把你的答案告诉我吧~ 💭"""

    async def _handle_answer(
        self,
        student_id: str,
        message: str,
        session: Session,
    ) -> str:
        """处理答题"""
        if not session.current_quiz:
            return '我现在没有题目给你做呢~ 说"出题"来获取题目吧！'

        quiz = session.current_quiz

        # 批改
        result = await self._grader_engine.grade(quiz, message)

        # 获取知识点
        student = await self._store.get_student(student_id)
        point_name = "数学题"

        # 保存记录
        await self._store.add_quiz_record(
            student_id=student_id,
            point_id="math_quiz",
            question=quiz.question,
            student_answer=message,
            is_correct=result.is_correct,
            feedback=result.feedback,
            difficulty=2,
        )

        # 清除当前题目
        session.current_quiz = None
        session.set_state(SessionState.IDLE)

        return f"""{result.feedback}

想继续做题就说"下一题"哦~ ✨"""

    async def _handle_explain(
        self,
        student_id: str,
        message: str,
        session: Session,
    ) -> str:
        """处理讲解请求"""
        # 调用LLM生成讲解
        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        explanation = response.choices[0].message.content
        return explanation

    async def _handle_diagnose(
        self,
        student_id: str,
        session: Session,
    ) -> str:
        """处理诊断请求"""
        student = await self._store.get_student(student_id)
        stats = await self._store.get_student_stats(student_id)

        if stats["total_quizzes"] < 3:
            return """你做得还不够多呢，先多做一些题我再帮你分析吧！📊

继续加油~ 💪"""

        report = await self._diagnose_engine.diagnose(
            student_id=student_id,
            grade=student.grade if student else 3,
            history_stats=stats,
            mastered_points=set(),  # 简化处理
        )

        # 生成友好输出
        output = [report.overall_summary, "\n"]

        if report.weak_points:
            output.append("🔍 薄弱点：")
            for wp in report.weak_points[:3]:
                output.append(f"  • {wp.point_name} (正确率{wp.accuracy:.0%})")

        if report.recommendations:
            output.append("\n💡 学习建议：")
            for rec in report.recommendations[:3]:
                output.append(f"  • {rec.suggested_action}")

        return "\n".join(output)

    async def _handle_chat(
        self,
        student_id: str,
        message: str,
        session: Session,
    ) -> str:
        """处理闲聊"""
        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.8,
            max_tokens=300,
        )

        return response.choices[0].message.content

    async def proactive_nudge(self, student_id: str) -> str:
        """主动推送"""
        student = await self._store.get_student(student_id)
        if not student:
            return "👋 好久不见！来学数学吧~"

        # 根据连胜天数生成不同消息
        if student.streak_days >= 7:
            return f"""🎉 连续学习{student.streak_days}天了！太厉害了！

今天的数学题等着你呢~ 📚✨"""
        elif student.streak_days >= 3:
            return f"""💪 你已经连续学习{student.streak_days}天了，继续保持！

今天想学什么？"""
        else:
            return "👋 你好呀！今天想学数学吗？来试试吧~ 📝"


# 默认教学Agent实例
_default_agent: TutorAgent | None = None


async def get_tutor_agent() -> TutorAgent:
    """获取默认教学Agent实例（懒加载）"""
    global _default_agent
    if _default_agent is None:
        _default_agent = TutorAgent()
    return _default_agent