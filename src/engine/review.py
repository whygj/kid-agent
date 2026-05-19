"""复习调度系统 - 基于艾宾浩斯遗忘曲线安排复习"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any

from src.knowledge.math_g3g5 import Difficulty


@dataclass
class ReviewItem:
    """复习项目"""
    point_id: str
    point_name: str
    next_review_date: datetime
    review_count: int
    last_reviewed: datetime | None = None
    mastery_level: int = 0  # 当前掌握程度
    interval: int = 1  # 当前复习间隔（天）


# 艾宾浩斯遗忘曲线复习间隔（天）
EBBINGHAUS_INTERVALS = [1, 3, 7, 14, 30]


class ReviewScheduler:
    """复习调度器 - 基于艾宾浩斯遗忘曲线"""

    def __init__(self, store=None):
        """初始化复习调度器

        Args:
            store: 存储实例（用于持久化复习计划）
        """
        self._store = store
        self._student_reviews: dict[str, dict[str, ReviewItem]] = {}

    def schedule_initial_review(
        self,
        student_id: str,
        point_id: str,
        point_name: str,
        mastery_level: int = 0,
    ) -> datetime:
        """安排初始复习

        Args:
            student_id: 学生ID
            point_id: 知识点ID
            point_name: 知识点名称
            mastery_level: 当前掌握程度

        Returns:
            datetime: 下次复习日期
        """
        # 计算下次复习日期（默认1天后）
        next_date = datetime.now() + timedelta(days=EBBINGHAUS_INTERVALS[0])

        item = ReviewItem(
            point_id=point_id,
            point_name=point_name,
            next_review_date=next_date,
            review_count=0,
            last_reviewed=None,
            mastery_level=mastery_level,
            interval=EBBINGHAUS_INTERVALS[0],
        )

        # 存储到内存
        if student_id not in self._student_reviews:
            self._student_reviews[student_id] = {}
        self._student_reviews[student_id][point_id] = item

        # 持久化到数据库
        if self._store:
            self._persist_review_schedule(student_id, item)

        return next_date

    def update_after_review(
        self,
        student_id: str,
        point_id: str,
        is_correct: bool,
        point_name: str | None = None,
    ) -> datetime | None:
        """复习后更新复习计划

        Args:
            student_id: 学生ID
            point_id: 知识点ID
            is_correct: 是否答对
            point_name: 知识点名称（可选）

        Returns:
            datetime | None: 更新后的下次复习日期
        """
        student_reviews = self._student_reviews.get(student_id, {})
        item = student_reviews.get(point_id)

        if not item:
            return None

        # 更新复习信息
        item.last_reviewed = datetime.now()
        item.review_count += 1

        # 根据答题结果调整间隔
        if is_correct:
            # 答对了，延后复习时间
            current_interval_index = self._get_interval_index(item.interval)
            if current_interval_index < len(EBBINGHAUS_INTERVALS) - 1:
                next_interval = EBBINGHAUS_INTERVALS[current_interval_index + 1]
            else:
                # 已经到了最长间隔，保持不变
                next_interval = item.interval
            item.interval = next_interval
        else:
            # 答错了，提前复习（回到前一个间隔）
            current_interval_index = self._get_interval_index(item.interval)
            if current_interval_index > 0:
                next_interval = EBBINGHAUS_INTERVALS[current_interval_index - 1]
            else:
                # 已经是最短间隔，保持不变
                next_interval = item.interval
            item.interval = next_interval

        # 计算下次复习日期
        item.next_review_date = datetime.now() + timedelta(days=item.interval)

        # 持久化到数据库
        if self._store:
            self._persist_review_schedule(student_id, item)

        return item.next_review_date

    def get_due_reviews(self, student_id: str) -> list[ReviewItem]:
        """获取今天需要复习的知识点

        Args:
            student_id: 学生ID

        Returns:
            list[ReviewItem]: 到期复习的项目列表
        """
        student_reviews = self._student_reviews.get(student_id, {})
        today = datetime.now().date()

        due_items = []
        for item in student_reviews.values():
            # 检查是否到期（下次复习日期在今天或之前）
            if item.next_review_date.date() <= today:
                due_items.append(item)

        # 按优先级排序：复习次数少的优先，掌握程度低的优先
        due_items.sort(key=lambda x: (x.review_count, -x.mastery_level))

        return due_items

    def get_all_reviews(self, student_id: str) -> list[ReviewItem]:
        """获取学生的所有复习计划

        Args:
            student_id: 学生ID

        Returns:
            list[ReviewItem]: 所有复习项目
        """
        return list(self._student_reviews.get(student_id, {}).values())

    def get_next_review_date(
        self,
        student_id: str,
        point_id: str,
    ) -> datetime | None:
        """获取指定知识点的下次复习日期

        Args:
            student_id: 学生ID
            point_id: 知识点ID

        Returns:
            datetime | None: 下次复习日期
        """
        item = self._student_reviews.get(student_id, {}).get(point_id)
        return item.next_review_date if item else None

    def cancel_review(
        self,
        student_id: str,
        point_id: str,
    ) -> bool:
        """取消复习计划（已完全掌握）

        Args:
            student_id: 学生ID
            point_id: 知识点ID

        Returns:
            bool: 是否成功取消
        """
        student_reviews = self._student_reviews.get(student_id, {})
        if point_id in student_reviews:
            del student_reviews[point_id]
            # TODO: 从数据库删除
            return True
        return False

    def load_student_reviews(self, student_id: str, reviews: list[Any]) -> None:
        """从数据库加载学生的复习计划

        Args:
            student_id: 学生ID
            reviews: 数据库返回的复习计划列表
        """
        if student_id not in self._student_reviews:
            self._student_reviews[student_id] = {}

        for review in reviews:
            item = ReviewItem(
                point_id=review.point_id,
                point_name="",  # 需要从知识点数据获取
                next_review_date=review.next_review_date,
                review_count=review.review_count,
                last_reviewed=review.last_reviewed,
                interval=1,  # 计算得出
            )

            # 计算间隔
            if review.last_reviewed and review.next_review_date:
                delta = (review.next_review_date - review.last_reviewed).days
                item.interval = delta if delta > 0 else 1

            self._student_reviews[student_id][review.point_id] = item

    def _get_interval_index(self, interval: int) -> int:
        """获取间隔在艾宾浩斯序列中的索引"""
        for i, val in enumerate(EBBINGHAUS_INTERVALS):
            if interval <= val:
                return i
        return len(EBBINGHAUS_INTERVALS) - 1

    def _persist_review_schedule(
        self,
        student_id: str,
        item: ReviewItem,
    ) -> None:
        """持久化复习计划到数据库"""
        if self._store:
            import asyncio
            asyncio.create_task(
                self._store.save_review_schedule(
                    student_id=student_id,
                    point_id=item.point_id,
                    next_review_date=item.next_review_date,
                    review_count=item.review_count,
                    last_reviewed=item.last_reviewed,
                )
            )


# 默认复习调度器实例
_default_scheduler: ReviewScheduler | None = None


def get_review_scheduler() -> ReviewScheduler:
    """获取默认复习调度器实例（懒加载）"""
    global _default_scheduler
    if _default_scheduler is None:
        _default_scheduler = ReviewScheduler()
    return _default_scheduler