"""家长学习通知"""

import logging
from datetime import datetime, timedelta

from src.wechat.client import get_wechat_client
from src.wechat.binding import get_user_binding

logger = logging.getLogger(__name__)


class ParentNotifier:
    """家长学习通知"""

    def __init__(self):
        """初始化通知器"""
        self.binding = get_user_binding()

    async def send_daily_report(self, student_id: str) -> bool:
        """发送每日学习报告给家长

        Args:
            student_id: 学生ID

        Returns:
            bool: 是否发送成功
        """
        # 获取家长微信ID
        parent_wechat_id = await self.binding.get_parent_binding(student_id)

        if not parent_wechat_id:
            logger.info(f"No parent binding for student {student_id}")
            return False

        # 生成报告
        report = await self._generate_report(student_id, "daily")
        if not report:
            return False

        # 发送消息
        client = await get_wechat_client()
        return await client.send_customer_message(parent_wechat_id, report)

    async def send_achievement(
        self, student_id: str, achievement: str, detail: str = ""
    ) -> bool:
        """发送成就通知（升级/连续答对等）

        Args:
            student_id: 学生ID
            achievement: 成就名称
            detail: 详细信息

        Returns:
            bool: 是否发送成功
        """
        parent_wechat_id = await self.binding.get_parent_binding(student_id)

        if not parent_wechat_id:
            return False

        message = f"🎉 {achievement}\n\n"
        if detail:
            message += f"{detail}\n\n"
        message += f"时间：{datetime.now().strftime('%H:%M')}"

        client = await get_wechat_client()
        return await client.send_customer_message(parent_wechat_id, message)

    async def send_level_up(self, student_id: str, level: int) -> bool:
        """发送升级通知

        Args:
            student_id: 学生ID
            level: 新等级

        Returns:
            bool: 是否发送成功
        """
        return await self.send_achievement(
            student_id,
            f"升级啦！🎖️ Lv.{level}",
            f"孩子成功升级到 {level} 级，继续加油！"
        )

    async def send_streak(self, student_id: str, streak_days: int) -> bool:
        """发送连续学习天数通知

        Args:
            student_id: 学生ID
            streak_days: 连续学习天数

        Returns:
            bool: 是否发送成功
        """
        if streak_days <= 1:
            return False

        achievement = f"连续学习 {streak_days} 天！🔥"
        detail = f"孩子已经连续学习 {streak_days} 天，太棒了！"

        return await self.send_achievement(student_id, achievement, detail)

    async def _generate_report(self, student_id: str, report_type: str = "daily") -> str | None:
        """生成学习报告

        Args:
            student_id: 学生ID
            report_type: 报告类型

        Returns:
            str | None: 报告文本
        """
        try:
            from src.agent.roster import get_student_roster

            roster = get_student_roster()
            roster._store = await self.binding._get_store()

            student = await roster._store.get_student(student_id)
            if not student:
                return None

            report = await roster.get_student_report(student_id)
            if not report:
                return None

            if report_type == "daily":
                time_range = "今日"
            else:
                time_range = "本周"

            response = (
                f"📊 {student.name} 的{time_range}学习报告\n"
                f"{'='*20}\n\n"
                f"🎖️ 等级：Lv.{report.level}\n"
                f"⭐ 经验：{report.total_xp} XP\n"
                f"🔥 连续学习：{report.streak_days} 天\n\n"
                f"📝 {time_range}统计：\n"
                f"• 答题数：{report.total_quizzes}\n"
                f"• 正确率：{report.correct_rate:.1%}\n\n"
            )

            if report.strong_points:
                response += f"💪 擅长：{', '.join(report.strong_points[:3])}\n"
            if report.weak_points:
                response += f"📖 需加强：{', '.join(report.weak_points[:3])}\n"

            response += f"\n报告时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"

            return response

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            return None


# 默认通知器实例
_default_notifier: ParentNotifier | None = None


def get_parent_notifier() -> ParentNotifier:
    """获取默认通知器实例（懒加载）"""
    global _default_notifier
    if _default_notifier is None:
        _default_notifier = ParentNotifier()
    return _default_notifier