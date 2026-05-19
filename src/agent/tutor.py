"""核心教学Agent - 协调所有引擎进行教学对话"""

import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from src.agent.intent import get_intent_recognizer, IntentResult
from src.agent.session import Session, SessionManager, SessionState
from src.config.settings import get_config
from src.engine.diagnose import get_diagnose_engine
from src.engine.explain import get_explain_engine, Explanation
from src.engine.grader import get_grader_engine, GradeResult
from src.engine.quiz import get_quiz_engine, Quiz
from src.knowledge.graph import KnowledgeGraph, get_graph
from src.knowledge.math_g3g5 import get_points_by_grade, ALL_POINTS, get_point_by_id
from src.memory.store import get_store, QuizHistoryORM
from src.memory.student import StudentModel, MasteryLevel


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
        self._intent_recognizer = None

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
        if self._intent_recognizer is None:
            self._intent_recognizer = get_intent_recognizer()

    def _build_messages(self, session: Session, user_message: str) -> list[dict]:
        """构建对话消息列表（包含历史上下文）"""
        messages = [{"role": "system", "content": self._system_prompt}]

        # 取最近20条消息作为上下文
        recent_messages = session.get_recent_messages(20)
        for msg in recent_messages:
            messages.append({"role": msg.role, "content": msg.content})

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        return messages

    async def start_session(self, student_id: str) -> str:
        """开始学习会话"""
        await self._get_engines()

        # 获取或创建学生
        student = await self._store.get_student(student_id)
        if not student:
            student = await self._store.create_student(student_id, "同学", 3)

        # 创建会话
        session = self.session_manager.create_session(student_id)

        # 加载掌握程度到 session metadata
        mastery_data = await self._store.get_mastery(student_id)
        session.metadata = {"mastery": mastery_data}

        # 生成开场白
        greeting = await self._generate_greeting(student, mastery_data)

        session.add_message("assistant", greeting, "command")
        session.set_state(SessionState.QUIZ)

        return greeting

    async def _generate_greeting(self, student, mastery_data: dict) -> str:
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

        # 统计掌握程度
        mastered = sum(1 for level in mastery_data.values() if level >= MasteryLevel.MASTERED.value)
        fuzzy = sum(1 for level in mastery_data.values() if level == MasteryLevel.FUZZY.value)

        if accuracy >= 0.8:
            emoji = "🌟"
            comment = "进步很大！"
        elif accuracy >= 0.6:
            emoji = "💪"
            comment = "继续保持！"
        else:
            emoji = "📚"
            comment = "加油加油！"

        mastery_info = ""
        if fuzzy > 0:
            mastery_info = f"\n还有{fuzzy}个知识点需要加强练习哦~"

        return f"""👋 欢迎回来！{emoji}

你最近完成了{recent_count}道题，正确率{accuracy:.0%}，{comment}{mastery_info}
已掌握{mastered}个知识点，继续加油！

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
        # 使用LLM意图识别
        result: IntentResult = await self._intent_recognizer.recognize(
            message,
            state=session.state.value,
        )

        # 特殊处理：在QUIZ状态下，如果识别为chat但置信度低，当作answer处理
        if session.state == SessionState.QUIZ and session.current_quiz:
            if result.intent == "chat" and result.confidence < 0.6:
                return "answer"

        return result.intent

    async def _handle_quiz(self, student_id: str, session: Session) -> str:
        """处理出题请求"""
        # 获取学生信息
        student = await self._store.get_student(student_id)
        grade = student.grade if student else 3

        # 获取年级知识点
        points = get_points_by_grade(grade)
        if not points:
            return "哎呀，还没有加载知识点呢~ 先休息一下吧 😴"

        # 获取掌握程度
        mastery_data = await self._store.get_mastery(student_id)
        session.metadata = {"mastery": mastery_data}

        # 优先选择薄弱点
        weak_points = [
            p for p in points
            if mastery_data.get(p.id, 0) in (
                MasteryLevel.FUZZY.value,
                MasteryLevel.FORGOTTEN.value,
            )
        ]

        # 获取上一题的知识点
        last_quiz = session.get_last_quiz()
        last_point_id = last_quiz.get("point_id") if last_quiz else None

        if weak_points:
            # 过滤掉上一题的知识点，避免重复
            candidates = [p for p in weak_points if p.id != last_point_id]
            if not candidates:
                candidates = weak_points
            point = candidates[len(session.messages) % len(candidates)]
        else:
            # 新学生或无薄弱点，按年级顺序出题
            candidates = [p for p in points if p.id != last_point_id]
            if not candidates:
                candidates = points
            point = candidates[len(session.messages) % len(candidates)]

        # 获取历史记录用于出题参考
        history = await self._store.get_student_history(student_id, limit=10)

        # 生成题目
        quiz = await self._quiz_engine.generate(point)

        # 保存当前题目
        session.current_quiz = quiz
        session.metadata["point_id"] = point.id
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
        point_id = session.metadata.get("point_id", "unknown")

        # 批改
        result = await self._grader_engine.grade(quiz, message)

        # 获取学生信息
        student = await self._store.get_student(student_id)

        # 保存答题记录
        await self._store.add_quiz_record(
            student_id=student_id,
            point_id=point_id,
            question=quiz.question,
            student_answer=message,
            is_correct=result.is_correct,
            feedback=result.feedback,
            difficulty=2,
        )

        # 持久化掌握程度
        new_level = MasteryLevel.UNKNOWN
        if result.is_correct:
            new_level = MasteryLevel.EXPOSING
        else:
            new_level = MasteryLevel.EXPOSING
        await self._store.save_mastery(student_id, point_id, new_level.value)

        # 更新学生XP
        old_xp = student.total_xp
        xp_gain = 10 if result.is_correct else 3
        if result.is_correct:
            student.total_xp += xp_gain
        else:
            student.total_xp += xp_gain
        await self._store.update_student_xp(student_id, xp_gain)

        # 检查升级
        level = 1 + student.total_xp // 100
        level_up_msg = ""
        if level > (1 + old_xp // 100):
            level_up_msg = f"\n\n🎉 恭喜你升到了{level}级！太棒了！"

        # 获取知识点名称
        point = get_point_by_id(point_id)
        point_name = point.name if point else "数学题"

        # 清除当前题目
        session.current_quiz = None
        session.set_state(SessionState.IDLE)

        response = f"""{result.feedback}

**{point_name}** 完成了！经验值+{xp_gain}{level_up_msg}

想继续做题就说"下一题"哦~ ✨"""
        return response

    async def _handle_explain(
        self,
        student_id: str,
        message: str,
        session: Session,
    ) -> str:
        """处理讲解请求"""
        # 使用对话历史
        messages = self._build_messages(session, message)

        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )

        return response.choices[0].message.content

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
        # 使用对话历史
        messages = self._build_messages(session, message)

        response = await self.client.chat.completions.create(
            model=self.config.llm.model,
            messages=messages,
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