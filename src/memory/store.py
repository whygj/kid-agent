"""持久化存储 - 使用SQLite存储学生数据"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, create_engine, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config.settings import get_config


class Base(DeclarativeBase):
    """SQLAlchemy Base类"""
    pass


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


# 默认存储实例
_default_store: MemoryStore | None = None


async def get_store() -> MemoryStore:
    """获取默认存储实例（懒加载）"""
    global _default_store
    if _default_store is None:
        _default_store = MemoryStore()
        await _default_store.init_db()
    return _default_store