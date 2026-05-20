"""持久化存储 - 使用SQLite存储学生数据"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, create_engine, func, select, Index
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config.settings import get_config


class Base(DeclarativeBase):
    """SQLAlchemy Base类"""
    pass


class WeChatBindingORM(Base):
    """微信绑定表"""
    __tablename__ = "wechat_bindings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wechat_user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_wechat_user_role", "wechat_user_id", "role", unique=True),
    )


class StudentORM(Base):
    """学生表"""
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)


class QuizHistoryORM(Base):
    """答题历史表"""
    __tablename__ = "quiz_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    point_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    student_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)


class MasteryORM(Base):
    """掌握程度表"""
    __tablename__ = "mastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    point_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mastery_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_student_point", "student_id", "point_id", unique=True),
    )


class ReviewScheduleORM(Base):
    """复习计划表"""
    __tablename__ = "review_schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    point_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    next_review_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_reviewed: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_review_student", "student_id", "next_review_date"),
        Index("idx_student_point_review", "student_id", "point_id", unique=True),
    )


class MemoryStore:
    """内存存储类"""

    def __init__(self, db_path: str | None = None):
        """初始化存储"""
        config = get_config()
        self.db_path = db_path or config.db.path

        # 确保数据目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # 异步引擎
        self._async_engine = create_async_engine(
            f"sqlite+aiosqlite:///{self.db_path}",
            echo=False,
        )
        self._async_sessionmaker = async_sessionmaker(
            self._async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init_db(self) -> None:
        """初始化数据库表"""
        async with self._async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """关闭数据库连接"""
        await self._async_engine.dispose()

    async def create_student(self, student_id: str, name: str, grade: int) -> StudentORM:
        """创建学生记录"""
        async with self._async_sessionmaker() as session:
            student = StudentORM(id=student_id, name=name, grade=grade)
            session.add(student)
            await session.commit()
            await session.refresh(student)
            return student

    async def get_student(self, student_id: str) -> StudentORM | None:
        """获取学生记录"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(StudentORM).where(StudentORM.id == student_id)
            )
            return result.scalar_one_or_none()

    async def update_student_xp(self, student_id: str, xp_delta: int) -> StudentORM | None:
        """更新学生经验值"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(StudentORM).where(StudentORM.id == student_id)
            )
            student = result.scalar_one_or_none()
            if student:
                student.total_xp += xp_delta
                student.updated_at = datetime.now()
                await session.commit()
                await session.refresh(student)
            return student

    async def update_student_streak(self, student_id: str, streak: int) -> StudentORM | None:
        """更新学生连续学习天数"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(StudentORM).where(StudentORM.id == student_id)
            )
            student = result.scalar_one_or_none()
            if student:
                student.streak_days = streak
                student.updated_at = datetime.now()
                await session.commit()
                await session.refresh(student)
            return student

    async def add_quiz_record(
        self,
        student_id: str,
        point_id: str,
        question: str,
        student_answer: str,
        is_correct: bool,
        feedback: str = "",
        difficulty: int = 2,
    ) -> QuizHistoryORM:
        """添加答题记录"""
        async with self._async_sessionmaker() as session:
            record = QuizHistoryORM(
                student_id=student_id,
                point_id=point_id,
                question=question,
                student_answer=student_answer,
                is_correct=is_correct,
                feedback=feedback,
                difficulty=difficulty,
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def get_student_history(
        self,
        student_id: str,
        limit: int = 100,
    ) -> list[QuizHistoryORM]:
        """获取学生答题历史"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(QuizHistoryORM)
                .where(QuizHistoryORM.student_id == student_id)
                .order_by(QuizHistoryORM.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def get_point_history(
        self,
        student_id: str,
        point_id: str,
    ) -> list[QuizHistoryORM]:
        """获取学生在某个知识点的答题历史"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(QuizHistoryORM)
                .where(
                    QuizHistoryORM.student_id == student_id,
                    QuizHistoryORM.point_id == point_id,
                )
                .order_by(QuizHistoryORM.created_at.desc())
            )
            return list(result.scalars().all())

    async def get_student_stats(self, student_id: str) -> dict[str, Any]:
        """获取学生统计信息"""
        async with self._async_sessionmaker() as session:
            # 总答题数
            total_result = await session.execute(
                select(func.count(QuizHistoryORM.id)).where(
                    QuizHistoryORM.student_id == student_id
                )
            )
            total = total_result.scalar() or 0

            # 正确数
            correct_result = await session.execute(
                select(func.count(QuizHistoryORM.id)).where(
                    QuizHistoryORM.student_id == student_id,
                    QuizHistoryORM.is_correct == True,
                )
            )
            correct = correct_result.scalar() or 0

            # 各知识点正确率
            point_stats = await session.execute(
                select(
                    QuizHistoryORM.point_id,
                    func.count(QuizHistoryORM.id).label("count"),
                    func.sum(QuizHistoryORM.is_correct).label("correct"),
                )
                .where(QuizHistoryORM.student_id == student_id)
                .group_by(QuizHistoryORM.point_id)
            )
            points = {}
            for row in point_stats:
                point_id = row.point_id
                count = row.count or 0
                correct_count = row.correct or 0
                points[point_id] = {
                    "total": count,
                    "correct": correct_count,
                    "accuracy": correct_count / count if count > 0 else 0,
                }

            # 最近学习时间
            recent_result = await session.execute(
                select(QuizHistoryORM.created_at)
                .where(QuizHistoryORM.student_id == student_id)
                .order_by(QuizHistoryORM.created_at.desc())
                .limit(1)
            )
            recent = recent_result.scalar_one_or_none()

            return {
                "total_quizzes": total,
                "correct_quizzes": correct,
                "accuracy": correct / total if total > 0 else 0,
                "point_stats": points,
                "last_activity": recent,
            }

    async def get_mastery(self, student_id: str) -> dict[str, int]:
        """获取学生所有知识点的掌握程度"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(MasteryORM).where(MasteryORM.student_id == student_id)
            )
            records = result.scalars().all()
            return {r.point_id: r.mastery_level for r in records}

    async def save_mastery(self, student_id: str, point_id: str, level: int) -> MasteryORM:
        """保存或更新知识点掌握程度"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(MasteryORM).where(
                    MasteryORM.student_id == student_id,
                    MasteryORM.point_id == point_id,
                )
            )
            mastery = result.scalar_one_or_none()

            if mastery:
                mastery.mastery_level = level
                mastery.updated_at = datetime.now()
            else:
                mastery = MasteryORM(
                    student_id=student_id,
                    point_id=point_id,
                    mastery_level=level,
                )
                session.add(mastery)

            await session.commit()
            await session.refresh(mastery)
            return mastery

    async def get_all_mastery(self, student_id: str) -> list[MasteryORM]:
        """获取学生所有掌握程度记录"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(MasteryORM).where(MasteryORM.student_id == student_id)
            )
            return list(result.scalars().all())

    async def save_review_schedule(
        self,
        student_id: str,
        point_id: str,
        next_review_date: datetime,
        review_count: int = 0,
        last_reviewed: datetime | None = None,
    ) -> ReviewScheduleORM:
        """保存或更新复习计划"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(ReviewScheduleORM).where(
                    ReviewScheduleORM.student_id == student_id,
                    ReviewScheduleORM.point_id == point_id,
                )
            )
            schedule = result.scalar_one_or_none()

            if schedule:
                schedule.next_review_date = next_review_date
                schedule.review_count = review_count
                schedule.last_reviewed = last_reviewed
                schedule.updated_at = datetime.now()
            else:
                schedule = ReviewScheduleORM(
                    student_id=student_id,
                    point_id=point_id,
                    next_review_date=next_review_date,
                    review_count=review_count,
                    last_reviewed=last_reviewed,
                )
                session.add(schedule)

            await session.commit()
            await session.refresh(schedule)
            return schedule

    async def get_review_schedule(
        self,
        student_id: str,
        point_id: str,
    ) -> ReviewScheduleORM | None:
        """获取指定知识点的复习计划"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(ReviewScheduleORM).where(
                    ReviewScheduleORM.student_id == student_id,
                    ReviewScheduleORM.point_id == point_id,
                )
            )
            return result.scalar_one_or_none()

    async def get_due_reviews(
        self,
        student_id: str,
        review_date: datetime | None = None,
    ) -> list[ReviewScheduleORM]:
        """获取到期的复习计划"""
        if review_date is None:
            review_date = datetime.now()

        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(ReviewScheduleORM)
                .where(
                    ReviewScheduleORM.student_id == student_id,
                    ReviewScheduleORM.next_review_date <= review_date,
                )
                .order_by(ReviewScheduleORM.review_count, ReviewScheduleORM.next_review_date)
            )
            return list(result.scalars().all())

    async def get_all_review_schedules(
        self,
        student_id: str,
    ) -> list[ReviewScheduleORM]:
        """获取学生的所有复习计划"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(ReviewScheduleORM)
                .where(ReviewScheduleORM.student_id == student_id)
                .order_by(ReviewScheduleORM.next_review_date)
            )
            return list(result.scalars().all())

    async def delete_review_schedule(
        self,
        student_id: str,
        point_id: str,
    ) -> bool:
        """删除复习计划"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(ReviewScheduleORM).where(
                    ReviewScheduleORM.student_id == student_id,
                    ReviewScheduleORM.point_id == point_id,
                )
            )
            schedule = result.scalar_one_or_none()
            if schedule:
                await session.delete(schedule)
                await session.commit()
                return True
            return False

    async def create_wechat_binding(
        self,
        wechat_user_id: str,
        student_id: str,
        role: str = "student",
    ) -> WeChatBindingORM:
        """创建微信绑定"""
        async with self._async_sessionmaker() as session:
            binding = WeChatBindingORM(
                wechat_user_id=wechat_user_id,
                student_id=student_id,
                role=role,
            )
            session.add(binding)
            await session.commit()
            await session.refresh(binding)
            return binding

    async def get_wechat_binding(
        self,
        wechat_user_id: str,
        role: str = "student",
    ) -> WeChatBindingORM | None:
        """获取微信绑定"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(WeChatBindingORM).where(
                    WeChatBindingORM.wechat_user_id == wechat_user_id,
                    WeChatBindingORM.role == role,
                )
            )
            return result.scalar_one_or_none()

    async def update_wechat_binding(
        self,
        wechat_user_id: str,
        student_id: str,
        role: str = "student",
    ) -> WeChatBindingORM | None:
        """更新微信绑定"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(WeChatBindingORM).where(
                    WeChatBindingORM.wechat_user_id == wechat_user_id,
                    WeChatBindingORM.role == role,
                )
            )
            binding = result.scalar_one_or_none()
            if binding:
                binding.student_id = student_id
                binding.created_at = datetime.now()
                await session.commit()
                await session.refresh(binding)
            return binding

    async def delete_wechat_binding(
        self,
        wechat_user_id: str,
        role: str = "student",
    ) -> bool:
        """删除微信绑定"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(WeChatBindingORM).where(
                    WeChatBindingORM.wechat_user_id == wechat_user_id,
                    WeChatBindingORM.role == role,
                )
            )
            binding = result.scalar_one_or_none()
            if binding:
                await session.delete(binding)
                await session.commit()
                return True
            return False

    async def get_wechat_binding_by_student(
        self,
        student_id: str,
        role: str = "student",
    ) -> WeChatBindingORM | None:
        """根据学生ID获取微信绑定"""
        async with self._async_sessionmaker() as session:
            result = await session.execute(
                select(WeChatBindingORM).where(
                    WeChatBindingORM.student_id == student_id,
                    WeChatBindingORM.role == role,
                )
            )
            return result.scalar_one_or_none()


# 默认存储实例
_default_store: MemoryStore | None = None


async def get_store() -> MemoryStore:
    """获取默认存储实例（懒加载）"""
    global _default_store
    if _default_store is None:
        _default_store = MemoryStore()
        await _default_store.init_db()
    return _default_store