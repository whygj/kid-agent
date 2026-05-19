"""测试数据库存储"""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from src.memory.student import MasteryLevel
from src.memory.store import (
    MasteryORM,
    MemoryStore,
    QuizHistoryORM,
    ReviewScheduleORM,
    StudentORM,
)


@pytest_asyncio.fixture
async def temp_store():
    """创建临时数据库存储"""
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        store = MemoryStore(str(db_path))
        await store.init_db()
        yield store
        await store.close()


class TestMemoryStore:
    """测试存储类"""

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_create_student(self, temp_store):
        """测试创建学生"""
        student = await temp_store.create_student("test_001", "测试学生", 3)

        assert student.id == "test_001"
        assert student.name == "测试学生"
        assert student.grade == 3
        assert student.total_xp == 0
        assert student.streak_days == 0
        assert isinstance(student.created_at, datetime)
        assert isinstance(student.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_create_duplicate_student(self, temp_store):
        """测试创建重复学生"""
        await temp_store.create_student("test_001", "学生1", 3)

        # 重复创建应报错
        with pytest.raises(Exception):
            await temp_store.create_student("test_001", "学生2", 4)

    @pytest.mark.asyncio
    async def test_get_student(self, temp_store):
        """测试获取学生"""
        await temp_store.create_student("test_001", "测试学生", 3)
        student = await temp_store.get_student("test_001")

        assert student is not None
        assert student.id == "test_001"
        assert student.name == "测试学生"

    @pytest.mark.asyncio
    async def test_get_nonexistent_student(self, temp_store):
        """测试获取不存在的学生"""
        student = await temp_store.get_student("nonexistent")
        assert student is None

    @pytest.mark.asyncio
    async def test_update_student_xp(self, temp_store):
        """测试更新学生经验值"""
        await temp_store.create_student("test_001", "测试学生", 3)

        student = await temp_store.update_student_xp("test_001", 50)
        assert student.total_xp == 50

        student = await temp_store.update_student_xp("test_001", 30)
        assert student.total_xp == 80

    @pytest.mark.asyncio
    async def test_update_student_xp_nonexistent(self, temp_store):
        """测试更新不存在学生的XP"""
        student = await temp_store.update_student_xp("nonexistent", 50)
        assert student is None

    @pytest.mark.asyncio
    async def test_update_student_streak(self, temp_store):
        """测试更新学生连续学习天数"""
        await temp_store.create_student("test_001", "测试学生", 3)

        student = await temp_store.update_student_streak("test_001", 7)
        assert student.streak_days == 7

    @pytest.mark.asyncio
    async def test_add_quiz_record(self, temp_store):
        """测试添加答题记录"""
        await temp_store.create_student("test_001", "测试学生", 3)

        record = await temp_store.add_quiz_record(
            student_id="test_001",
            point_id="math_g3_001",
            question="5 × 6 = ?",
            student_answer="30",
            is_correct=True,
            feedback="太棒了！",
            difficulty=2,
        )

        assert record.id > 0
        assert record.student_id == "test_001"
        assert record.point_id == "math_g3_001"
        assert record.question == "5 × 6 = ?"
        assert record.student_answer == "30"
        assert record.is_correct is True or record.is_correct == 1
        assert record.feedback == "太棒了！"
        assert record.difficulty == 2
        assert isinstance(record.created_at, datetime)

    @pytest.mark.asyncio
    async def test_get_student_history(self, temp_store):
        """测试获取学生答题历史"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # 添加3条记录
        for i in range(3):
            await temp_store.add_quiz_record(
                student_id="test_001",
                point_id="math_g3_001",
                question=f"题{i}",
                student_answer=str(i),
                is_correct=i % 2 == 0,
                feedback="",
                difficulty=2,
            )

        history = await temp_store.get_student_history("test_001")
        assert len(history) == 3
        # 应按时间倒序排列
        assert history[0].question == "题2"

    @pytest.mark.asyncio
    async def test_get_student_history_limit(self, temp_store):
        """测试获取限制数量的历史记录"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # 添加10条记录
        for i in range(10):
            await temp_store.add_quiz_record(
                student_id="test_001",
                point_id="math_g3_001",
                question=f"题{i}",
                student_answer=str(i),
                is_correct=True,
                feedback="",
                difficulty=2,
            )

        history = await temp_store.get_student_history("test_001", limit=5)
        assert len(history) == 5

    @pytest.mark.asyncio
    async def test_get_point_history(self, temp_store):
        """测试获取知识点历史记录"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # 添加不同知识点的记录
        await temp_store.add_quiz_record(
            student_id="test_001",
            point_id="math_g3_001",
            question="题1",
            student_answer="1",
            is_correct=True,
            feedback="",
            difficulty=2,
        )
        await temp_store.add_quiz_record(
            student_id="test_001",
            point_id="math_g3_002",
            question="题2",
            student_answer="2",
            is_correct=True,
            feedback="",
            difficulty=2,
        )
        await temp_store.add_quiz_record(
            student_id="test_001",
            point_id="math_g3_001",
            question="题3",
            student_answer="3",
            is_correct=False,
            feedback="",
            difficulty=2,
        )

        history = await temp_store.get_point_history("test_001", "math_g3_001")
        assert len(history) == 2

    @pytest.mark.asyncio
    async def test_get_student_stats(self, temp_store):
        """测试获取学生统计信息"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # 添加10条记录（6对4错）
        for i in range(10):
            await temp_store.add_quiz_record(
                student_id="test_001",
                point_id="math_g3_001" if i < 5 else "math_g3_002",
                question=f"题{i}",
                student_answer=str(i),
                is_correct=i < 6,
                feedback="",
                difficulty=2,
            )

        stats = await temp_store.get_student_stats("test_001")

        assert stats["total_quizzes"] == 10
        assert stats["correct_quizzes"] == 6
        assert stats["accuracy"] == 0.6
        assert "point_stats" in stats
        assert "last_activity" in stats

    @pytest.mark.asyncio
    async def test_get_student_stats_empty(self, temp_store):
        """测试获取空学生统计"""
        await temp_store.create_student("test_001", "测试学生", 3)

        stats = await temp_store.get_student_stats("test_001")

        assert stats["total_quizzes"] == 0
        assert stats["correct_quizzes"] == 0
        assert stats["accuracy"] == 0.0

    @pytest.mark.asyncio
    async def test_save_mastery_new(self, temp_store):
        """测试保存新掌握程度"""
        await temp_store.create_student("test_001", "测试学生", 3)

        mastery = await temp_store.save_mastery(
            student_id="test_001",
            point_id="math_g3_001",
            level=MasteryLevel.MASTERED.value,
        )

        assert mastery.student_id == "test_001"
        assert mastery.point_id == "math_g3_001"
        assert mastery.mastery_level == MasteryLevel.MASTERED.value

    @pytest.mark.asyncio
    async def test_save_mastery_update(self, temp_store):
        """测试更新掌握程度"""
        await temp_store.create_student("test_001", "测试学生", 3)
        await temp_store.save_mastery(
            student_id="test_001",
            point_id="math_g3_001",
            level=1,
        )

        # 更新
        mastery = await temp_store.save_mastery(
            student_id="test_001",
            point_id="math_g3_001",
            level=3,
        )

        assert mastery.mastery_level == 3

    @pytest.mark.asyncio
    async def test_get_mastery(self, temp_store):
        """测试获取掌握程度"""
        await temp_store.create_student("test_001", "测试学生", 3)

        await temp_store.save_mastery("test_001", "math_g3_001", 2)
        await temp_store.save_mastery("test_001", "math_g3_002", 3)
        await temp_store.save_mastery("test_001", "math_g3_003", 1)

        mastery_dict = await temp_store.get_mastery("test_001")

        assert len(mastery_dict) == 3
        assert mastery_dict["math_g3_001"] == 2
        assert mastery_dict["math_g3_002"] == 3
        assert mastery_dict["math_g3_003"] == 1

    @pytest.mark.asyncio
    async def test_get_mastery_empty(self, temp_store):
        """测试获取空掌握程度"""
        await temp_store.create_student("test_001", "测试学生", 3)

        mastery_dict = await temp_store.get_mastery("test_001")
        assert len(mastery_dict) == 0

    @pytest.mark.asyncio
    async def test_get_all_mastery(self, temp_store):
        """测试获取所有掌握程度记录"""
        await temp_store.create_student("test_001", "测试学生", 3)

        await temp_store.save_mastery("test_001", "math_g3_001", 2)
        await temp_store.save_mastery("test_001", "math_g3_002", 3)

        records = await temp_store.get_all_mastery("test_001")

        assert len(records) == 2
        assert all(r.student_id == "test_001" for r in records)

    @pytest.mark.asyncio
    async def test_save_review_schedule_new(self, temp_store):
        """测试保存新复习计划"""
        await temp_store.create_student("test_001", "测试学生", 3)

        next_date = datetime.now() + timedelta(days=1)
        schedule = await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_001",
            next_review_date=next_date,
            review_count=0,
        )

        assert schedule.student_id == "test_001"
        assert schedule.point_id == "math_g3_001"
        assert schedule.review_count == 0
        assert schedule.last_reviewed is None

    @pytest.mark.asyncio
    async def test_save_review_schedule_update(self, temp_store):
        """测试更新复习计划"""
        await temp_store.create_student("test_001", "测试学生", 3)

        next_date1 = datetime.now() + timedelta(days=1)
        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_001",
            next_review_date=next_date1,
            review_count=0,
        )

        next_date2 = datetime.now() + timedelta(days=3)
        schedule = await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_001",
            next_review_date=next_date2,
            review_count=1,
            last_reviewed=datetime.now(),
        )

        assert schedule.review_count == 1
        assert schedule.last_reviewed is not None

    @pytest.mark.asyncio
    async def test_get_review_schedule(self, temp_store):
        """测试获取复习计划"""
        await temp_store.create_student("test_001", "测试学生", 3)

        next_date = datetime.now() + timedelta(days=1)
        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_001",
            next_review_date=next_date,
            review_count=0,
        )

        schedule = await temp_store.get_review_schedule("test_001", "math_g3_001")

        assert schedule is not None
        assert schedule.point_id == "math_g3_001"

    @pytest.mark.asyncio
    async def test_get_review_schedule_nonexistent(self, temp_store):
        """测试获取不存在的复习计划"""
        await temp_store.create_student("test_001", "测试学生", 3)

        schedule = await temp_store.get_review_schedule("test_001", "math_g3_001")
        assert schedule is None

    @pytest.mark.asyncio
    async def test_get_due_reviews(self, temp_store):
        """测试获取到期复习"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # 今天到期
        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_001",
            next_review_date=datetime.now(),
            review_count=0,
        )
        # 明天到期
        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_002",
            next_review_date=datetime.now() + timedelta(days=1),
            review_count=0,
        )
        # 昨天到期
        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_003",
            next_review_date=datetime.now() - timedelta(days=1),
            review_count=0,
        )

        due_reviews = await temp_store.get_due_reviews("test_001")

        assert len(due_reviews) == 2  # 今天和昨天

    @pytest.mark.asyncio
    async def test_get_all_review_schedules(self, temp_store):
        """测试获取所有复习计划"""
        await temp_store.create_student("test_001", "测试学生", 3)

        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_001",
            next_review_date=datetime.now() + timedelta(days=1),
            review_count=0,
        )
        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_002",
            next_review_date=datetime.now() + timedelta(days=3),
            review_count=0,
        )

        schedules = await temp_store.get_all_review_schedules("test_001")

        assert len(schedules) == 2

    @pytest.mark.asyncio
    async def test_delete_review_schedule(self, temp_store):
        """测试删除复习计划"""
        await temp_store.create_student("test_001", "测试学生", 3)

        await temp_store.save_review_schedule(
            student_id="test_001",
            point_id="math_g3_001",
            next_review_date=datetime.now() + timedelta(days=1),
            review_count=0,
        )

        deleted = await temp_store.delete_review_schedule("test_001", "math_g3_001")
        assert deleted is True

        schedule = await temp_store.get_review_schedule("test_001", "math_g3_001")
        assert schedule is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_review_schedule(self, temp_store):
        """测试删除不存在的复习计划"""
        deleted = await temp_store.delete_review_schedule("test_001", "math_g3_001")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_mastery_persistence(self, temp_store):
        """测试掌握程度持久化"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # 保存
        await temp_store.save_mastery("test_001", "math_g3_001", 3)

        # 读取
        mastery_dict = await temp_store.get_mastery("test_001")

        assert mastery_dict["math_g3_001"] == 3

    @pytest.mark.asyncio
    async def test_quiz_history_query(self, temp_store):
        """测试答题历史查询"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # 添加记录
        for i in range(5):
            await temp_store.add_quiz_record(
                student_id="test_001",
                point_id="math_g3_001" if i < 3 else "math_g3_002",
                question=f"题{i}",
                student_answer=str(i),
                is_correct=i % 2 == 0,
                feedback="",
                difficulty=2,
            )

        # 获取历史
        history = await temp_store.get_student_history("test_001", limit=10)

        assert len(history) == 5
        assert sum(1 for h in history if h.is_correct) == 3

    @pytest.mark.asyncio
    async def test_point_accuracy_stats(self, temp_store):
        """测试知识点正确率统计"""
        await temp_store.create_student("test_001", "测试学生", 3)

        # math_g3_001: 5题，3对2错
        for i in range(5):
            await temp_store.add_quiz_record(
                student_id="test_001",
                point_id="math_g3_001",
                question=f"题{i}",
                student_answer=str(i),
                is_correct=i < 3,
                feedback="",
                difficulty=2,
            )

        # math_g3_002: 4题，4对0错
        for i in range(4):
            await temp_store.add_quiz_record(
                student_id="test_001",
                point_id="math_g3_002",
                question=f"题{i+5}",
                student_answer=str(i),
                is_correct=True,
                feedback="",
                difficulty=2,
            )

        stats = await temp_store.get_student_stats("test_001")
        point_stats = stats["point_stats"]

        assert point_stats["math_g3_001"]["total"] == 5
        assert point_stats["math_g3_001"]["correct"] == 3
        assert abs(point_stats["math_g3_001"]["accuracy"] - 0.6) < 0.01

        assert point_stats["math_g3_002"]["total"] == 4
        assert point_stats["math_g3_002"]["correct"] == 4
        assert point_stats["math_g3_002"]["accuracy"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
