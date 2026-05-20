"""微信消息处理器"""

import logging
import re
from datetime import datetime

from src.agent.tutor import get_tutor_agent
from src.agent.roster import get_student_roster
from src.knowledge.math_g3g5 import ALL_POINTS
from src.wechat.binding import get_user_binding

logger = logging.getLogger(__name__)


class WeChatHandler:
    """微信消息处理器"""

    def __init__(self):
        """初始化处理器"""
        self.binding = get_user_binding()

    async def handle_text(self, user_id: str, content: str) -> str:
        """处理文本消息

        Args:
            user_id: 微信用户OpenID
            content: 消息内容

        Returns:
            str: 回复内容
        """
        content = content.strip()

        # 绑定命令：绑定 学生ID
        if content.startswith("绑定 ") or content.startswith("bind "):
            parts = content.split(maxsplit=1)
            if len(parts) == 2:
                student_id = parts[1].strip()
                return await self.binding.bind(user_id, student_id, "student")
            return "请使用格式：绑定 <学生ID>"

        # 家长绑定命令：家长绑定 学生ID
        if content.startswith("家长绑定 ") or content.startswith("parent "):
            parts = content.split(maxsplit=1)
            if len(parts) == 2:
                student_id = parts[1].strip()
                return await self.binding.bind(user_id, student_id, "parent")
            return "请使用格式：家长绑定 <学生ID>"

        # 帮助命令
        if content in ["帮助", "help", "?", "？"]:
            return self._get_help_message()

        # 查找绑定的学生ID
        student_id = await self.binding.get_student_id(user_id, "student")

        if not student_id:
            return (
                "你还没有绑定学生账号哦~\n\n"
                "请使用「绑定 <学生ID>」命令来绑定你的账号\n"
                "例如：绑定 student01\n\n"
                "输入「帮助」查看更多命令"
            )

        # 调用 TutorAgent 处理消息
        try:
            agent = await get_tutor_agent()
            response = await agent.chat(student_id, content)
            return response
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return "出错了，请稍后再试~"

    async def handle_event(self, user_id: str, event: str, event_key: str) -> str:
        """处理事件消息

        Args:
            user_id: 微信用户OpenID
            event: 事件类型（subscribe/unsubscribe/CLICK等）
            event_key: 事件KEY

        Returns:
            str: 回复内容
        """
        if event == "subscribe":
            return await self._handle_subscribe(user_id)
        elif event == "unsubscribe":
            return await self._handle_unsubscribe(user_id)
        elif event == "CLICK":
            return await self._handle_click(user_id, event_key)
        else:
            logger.info(f"Unhandled event: {event}, key: {event_key}")
            return "收到你的消息啦~"

    async def handle_voice(self, user_id: str, xml_data: str) -> str:
        """处理语音消息

        Args:
            user_id: 微信用户OpenID
            xml_data: XML消息数据

        Returns:
            str: 回复内容
        """
        # 语音识别结果在 Recognition 字段
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(xml_data)
            recognition = root.findtext("Recognition", "")
            if recognition:
                logger.info(f"Voice recognition: {recognition}")
                return await self.handle_text(user_id, recognition)
        except Exception as e:
            logger.error(f"Error parsing voice message: {e}")

        return "语音识别失败，请用文字输入吧~"

    async def _handle_subscribe(self, user_id: str) -> str:
        """处理关注事件"""
        logger.info(f"User {user_id} subscribed")

        welcome = (
            "欢迎关注 Kid Agent！🎉\n\n"
            "我是你的小学数学学习小助手~\n\n"
            "📚 主要功能：\n"
            "• 智能出题：根据你的水平出题\n"
            "• 自适应学习：难度自动调整\n"
            "• 薄弱诊断：找出需要加强的知识点\n"
            "• 学习报告：查看学习进度\n\n"
            "👉 使用「绑定 <学生ID>」开始学习\n"
            "例如：绑定 student01\n\n"
            "输入「帮助」查看更多命令"
        )
        return welcome

    async def _handle_unsubscribe(self, user_id: str) -> str:
        """处理取消关注事件"""
        logger.info(f"User {user_id} unsubscribed")
        return ""

    async def _handle_click(self, user_id: str, event_key: str) -> str:
        """处理菜单点击事件"""
        if event_key == "start_learn":
            return await self._handle_start_learn(user_id)
        elif event_key == "today_report":
            return await self._handle_today_report(user_id)
        elif event_key == "weekly_report":
            return await self._handle_weekly_report(user_id)
        elif event_key == "help":
            return self._get_help_message()
        else:
            return "收到你的点击~"

    async def _handle_start_learn(self, user_id: str) -> str:
        """处理开始学习菜单点击"""
        student_id = await self.binding.get_student_id(user_id, "student")

        if not student_id:
            return (
                "你还没有绑定学生账号哦~\n\n"
                "请使用「绑定 <学生ID>」命令来绑定你的账号"
            )

        try:
            agent = await get_tutor_agent()
            greeting = await agent.start_session(student_id)
            return greeting
        except Exception as e:
            logger.error(f"Error starting session: {e}", exc_info=True)
            return "出错了，请稍后再试~"

    async def _handle_today_report(self, user_id: str) -> str:
        """处理今日报告菜单点击"""
        student_id = await self.binding.get_student_id(user_id, "student")

        if not student_id:
            return "你还没有绑定学生账号哦~"

        try:
            roster = get_student_roster()
            roster._store = await self.binding._get_store()
            report = await roster.get_student_report(student_id)

            if not report:
                return "还没有学习记录呢，开始学习吧！"

            student = await roster._store.get_student(student_id)
            name = student.name if student else "你"

            response = (
                f"📊 {name} 的学习报告\n\n"
                f"🎖️ 等级：{report.level}级\n"
                f"⭐ 总经验：{report.total_xp} XP\n"
                f"🔥 连续学习：{report.streak_days} 天\n"
                f"📝 总答题数：{report.total_quizzes}\n"
                f"✅ 正确率：{report.correct_rate:.1%}\n\n"
            )

            if report.strong_points:
                response += f"💪 擅长：{', '.join(report.strong_points)}\n"
            if report.weak_points:
                response += f"📖 需加强：{', '.join(report.weak_points)}\n"

            return response

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            return "出错了，请稍后再试~"

    async def _handle_weekly_report(self, user_id: str) -> str:
        """处理周报菜单点击"""
        student_id = await self.binding.get_student_id(user_id, "student")

        if not student_id:
            return "你还没有绑定学生账号哦~"

        try:
            roster = get_student_roster()
            roster._store = await self.binding._get_store()

            report = await roster.get_student_report(student_id)
            if not report:
                return "还没有学习记录呢，开始学习吧！"

            student = await roster._store.get_student(student_id)
            name = student.name if student else "你"

            response = (
                f"📈 {name} 的周度报告\n\n"
                f"本周学习统计：\n"
                f"• 总答题数：{report.total_quizzes}\n"
                f"• 正确率：{report.correct_rate:.1%}\n"
                f"• 当前等级：{report.level}级\n"
                f"• 连续学习：{report.streak_days} 天\n\n"
            )

            response += f"知识掌握情况（共{len(ALL_POINTS)}个知识点）：\n"
            for point_id, info in report.mastery.items():
                if info["level"] > 0:
                    point = next((p for p in ALL_POINTS if p.id == point_id), None)
                    point_name = point.name if point else point_id
                    response += f"• {point_name}: {info['level']}★\n"

            return response

        except Exception as e:
            logger.error(f"Error generating weekly report: {e}", exc_info=True)
            return "出错了，请稍后再试~"

    def _get_help_message(self) -> str:
        """获取帮助消息"""
        return (
            "📖 帮助\n\n"
            "🔹 绑定账号\n"
            "「绑定 <学生ID>」 - 绑定学生账号\n"
            "「家长绑定 <学生ID>」 - 家长绑定学生\n\n"
            "🔹 开始学习\n"
            "直接发消息，我会根据你的情况出题\n"
            "或点击「开始学习」菜单\n\n"
            "🔹 查看报告\n"
            "「今日报告」 - 查看今日学习进度\n"
            "「学习周报」 - 查看周度学习报告\n\n"
            "🔹 学习命令\n"
            "「做题」 - 出一道题\n"
            "「讲解 <知识点>」 - 讲解某个知识点\n"
            "「诊断」 - 查看薄弱点\n"
        )