"""测试学生模型和掌握程度"""

import pytest
from datetime import datetime, timedelta

from src.memory.student import (
    MasteryLevel,
    QuizRecord,
    StudentModel,
)


class TestMasteryLevel:
    """测试掌握程度枚举"""

    def test_mastery_level_values(self):
        """测试掌握程度数值"""
        assert MasteryLevel.UNKNOWN == 0
        assert MasteryLevel.EXPOSING == 1
        assert MasteryLevel.FUZZY == 2
        assert MasteryLevel.MASTERED == 3
        assert MasteryLevel.FORGOTTEN == 4


class TestQuizRecord:
    """测试答题记录"""

    def test_quiz_record_creation(self):
        """测试答题记录创建"""
        record = QuizRecord(
            point_id="math_g3_001",
            question="5 × 6 = ?",
            answer="30",
            is_correct=True,
            feedback="太棒了！",
            difficulty=2,
        )

        assert record.point_id == "math_g3_001"
        assert record.question == "5 × 6 = ?"
        assert record.answer == "30"
        assert record.is_correct is True
        assert record.feedback == "太棒了！"
        assert record.difficulty == 2

    def test_quiz_record_default_timestamp(self):
        """测试答题记录默认时间戳"""
        before = datetime.now()
        record = QuizRecord(
            point_id="test",
            question="?",
            answer="?",
            is_correct=False,
            feedback="",
            difficulty=2,
        )
        after = datetime.now()

        assert before <= record.timestamp <= after


class TestStudentModel:
    """测试学生模型"""

    @pytest.fixture
    def student(self):
        """创建测试学生"""
        return StudentModel(
            id="test_student",
            name="测试学生",
            grade=3,
        )

    def test_student_creation(self, student):
        """测试学生创建"""
        assert student.id == "test_student"
        assert student.name == "测试学生"
        assert student.grade == 3
        assert len(student.mastery) == 0
        assert len(student.history) == 0
        assert student.total_xp == 0
        assert student.streak_days == 0
        assert student.consecutive_correct == 0
        assert student.level == 1

    def test_get_mastery_unknown(self, student):
        """测试获取未知掌握程度"""
        mastery = student.get_mastery("math_g3_001")
        assert mastery == MasteryLevel.UNKNOWN

    def test_get_mastery_after_set(self, student):
        """测试设置后获取掌握程度"""
        student.mastery["math_g3_001"] = MasteryLevel.MASTERED
        mastery = student.get_mastery("math_g3_001")
        assert mastery == MasteryLevel.MASTERED

    def test_update_mastery_from_unknown(self, student):
        """测试从未知状态更新掌握程度"""
        # 首次答对
        new_level = student.update_mastery("math_g3_001", True)
        assert new_level == MasteryLevel.EXPOSING

        # 首次答错
        new_level = student.update_mastery("math_g3_002", False)
        assert new_level == MasteryLevel.EXPOSING

    def test_update_mastery_to_fuzzy(self, student):
        """测试更新到模糊状态"""
        student.mastery["math_g3_001"] = MasteryLevel.EXPOSING

        # 答对2题达到模糊状态
        for _ in range(2):
            student.add_record(QuizRecord(
                point_id="math_g3_001",
                question="?",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        assert student.get_mastery("math_g3_001") == MasteryLevel.FUZZY

    def test_update_mastery_to_mastered(self, student):
        """测试更新到掌握状态"""
        student.mastery["math_g3_001"] = MasteryLevel.FUZZY

        # 答对5题达到掌握状态
        for _ in range(5):
            student.add_record(QuizRecord(
                point_id="math_g3_001",
                question="?",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        assert student.get_mastery("math_g3_001") == MasteryLevel.MASTERED

    def test_update_mastery_from_mastered_to_forgotten(self, student):
        """测试从掌握状态到遗忘"""
        student.mastery["math_g3_001"] = MasteryLevel.MASTERED

        # 添加历史记录（7天前）
        old_record = QuizRecord(
            point_id="math_g3_001",
            question="?",
            answer="?",
            is_correct=True,
            feedback="",
            difficulty=2,
        )
        old_record.timestamp = datetime.now() - timedelta(days=10)
        student.history.append(old_record)

        # 答错一道题
        new_level = student.update_mastery("math_g3_001", False)
        assert new_level == MasteryLevel.FORGOTTEN

    def test_update_mastery_from_mastered_to_fuzzy(self, student):
        """测试从掌握状态到模糊（未超期）"""
        student.mastery["math_g3_001"] = MasteryLevel.MASTERED

        # 添加历史记录（1天前）
        old_record = QuizRecord(
            point_id="math_g3_001",
            question="?",
            answer="?",
            is_correct=True,
            feedback="",
            difficulty=2,
        )
        old_record.timestamp = datetime.now() - timedelta(days=1)
        student.history.append(old_record)

        # 答错一道题
        new_level = student.update_mastery("math_g3_001", False)
        assert new_level == MasteryLevel.FUZZY

    def test_update_mastery_from_forgotten_to_fuzzy(self, student):
        """测试从遗忘状态回到模糊"""
        student.mastery["math_g3_001"] = MasteryLevel.FORGOTTEN

        # 答对1题回到模糊状态
        student.add_record(QuizRecord(
            point_id="math_g3_001",
            question="?",
            answer="?",
            is_correct=True,
            feedback="",
            difficulty=2,
        ))

        assert student.get_mastery("math_g3_001") == MasteryLevel.FUZZY

    def test_add_record_correct(self, student):
        """测试添加正确答题记录"""
        xp_gain, new_level, message = student.add_record(QuizRecord(
            point_id="math_g3_001",
            question="5 × 6 = ?",
            answer="30",
            is_correct=True,
            feedback="太棒了！",
            difficulty=2,
        ))

        assert xp_gain == 10
        assert new_level == 1
        assert message == ""
        assert student.total_xp == 10
        assert student.consecutive_correct == 1
        assert len(student.history) == 1

    def test_add_record_wrong(self, student):
        """测试添加错误答题记录"""
        xp_gain, new_level, message = student.add_record(QuizRecord(
            point_id="math_g3_001",
            question="5 × 6 = ?",
            answer="35",
            is_correct=False,
            feedback="再想想",
            difficulty=2,
        ))

        assert xp_gain == 3
        assert new_level == 1
        assert student.consecutive_correct == 0
        assert len(student.history) == 1

    def test_xp_streak_bonus_3(self, student):
        """测试3连对加成"""
        for _ in range(3):
            xp_gain, _, _ = student.add_record(QuizRecord(
                point_id="math_g3_001",
                question="?",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        # 3连对后XP应该是15
        last_record = student.history[-1]
        assert last_record.is_correct
        assert student.consecutive_correct == 3

        # 下一次答题XP应该是15
        xp_gain, _, _ = student.add_record(QuizRecord(
            point_id="math_g3_001",
            question="?",
            answer="?",
            is_correct=True,
            feedback="",
            difficulty=2,
        ))
        assert xp_gain == 15

    def test_xp_streak_bonus_5(self, student):
        """测试5连对加成"""
        for _ in range(5):
            student.add_record(QuizRecord(
                point_id="math_g3_001",
                question="?",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        # 5连对后XP应该是20
        xp_gain, _, _ = student.add_record(QuizRecord(
            point_id="math_g3_001",
            question="?",
            answer="?",
            is_correct=True,
            feedback="",
            difficulty=2,
        ))
        assert xp_gain == 20

    def test_level_up(self, student):
        """测试升级"""
        # 达到一定XP后应该升级到2级
        # 预期：前2题各10 XP，第3-4题各15 XP，第5-10题各20 XP
        # 总计：20 + 30 + 120 = 170 XP
        for i in range(10):
            xp_gain, new_level, message = student.add_record(QuizRecord(
                point_id="math_g3_001",
                question=f"题{i}",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        assert student.total_xp == 170  # 计算连对加成后的总XP
        assert student.level == 2

        # 应该有升级消息
        _, _, message = student.add_record(QuizRecord(
            point_id="math_g3_001",
            question="? ?",
            answer="?",
            is_correct=True,
            feedback="",
            difficulty=2,
        ))
        # 已经是2级，再答一题到了190 XP，仍在2级范围内
        assert student.total_xp == 190

    def test_get_weak_points(self, student):
        """测试获取薄弱点"""
        student.mastery["math_g3_001"] = MasteryLevel.FUZZY
        student.mastery["math_g3_002"] = MasteryLevel.FORGOTTEN
        student.mastery["math_g3_003"] = MasteryLevel.MASTERED

        weak = student.get_weak_points()
        assert "math_g3_001" in weak
        assert "math_g3_002" in weak
        assert "math_g3_003" not in weak

    def test_get_mastered_points(self, student):
        """测试获取已掌握知识点"""
        student.mastery["math_g3_001"] = MasteryLevel.MASTERED
        student.mastery["math_g3_002"] = MasteryLevel.FUZZY
        student.mastery["math_g3_003"] = MasteryLevel.FORGOTTEN

        mastered = student.get_mastered_points()
        assert "math_g3_001" in mastered
        assert "math_g3_002" not in mastered
        assert "math_g3_003" not in mastered

    def test_get_accuracy_empty(self, student):
        """测试空历史正确率"""
        accuracy = student.get_accuracy()
        assert accuracy == 0.0

    def test_get_accuracy_all_correct(self, student):
        """测试全部正确率"""
        for _ in range(5):
            student.add_record(QuizRecord(
                point_id="math_g3_001",
                question="?",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        accuracy = student.get_accuracy()
        assert accuracy == 1.0

    def test_get_accuracy_mixed(self, student):
        """测试混合正确率"""
        for i in range(10):
            student.add_record(QuizRecord(
                point_id="math_g3_001",
                question=f"题{i}",
                answer="?",
                is_correct=i % 2 == 0,
                feedback="",
                difficulty=2,
            ))

        accuracy = student.get_accuracy()
        assert accuracy == 0.5

    def test_get_accuracy_by_point(self, student):
        """测试按知识点获取正确率"""
        # math_g3_001 5题全对
        for _ in range(5):
            student.add_record(QuizRecord(
                point_id="math_g3_001",
                question="?",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        # math_g3_002 5题全错
        for _ in range(5):
            student.add_record(QuizRecord(
                point_id="math_g3_002",
                question="?",
                answer="?",
                is_correct=False,
                feedback="",
                difficulty=2,
            ))

        accuracy_001 = student.get_accuracy("math_g3_001")
        accuracy_002 = student.get_accuracy("math_g3_002")

        assert accuracy_001 == 1.0
        assert accuracy_002 == 0.0

    def test_to_dict(self, student):
        """测试导出为字典"""
        student.mastery["math_g3_001"] = MasteryLevel.MASTERED
        student.total_xp = 150
        student.streak_days = 5

        data = student.to_dict()

        assert data["id"] == "test_student"
        assert data["name"] == "测试学生"
        assert data["grade"] == 3
        assert data["mastery"]["math_g3_001"] == MasteryLevel.MASTERED.value
        assert data["total_xp"] == 150
        assert data["streak_days"] == 5
        assert "last_activity" in data

    def test_consecutive_correct_reset_on_wrong(self, student):
        """测试答错后重置连对计数"""
        # 连对3题
        for _ in range(3):
            student.add_record(QuizRecord(
                point_id="math_g3_001",
                question="?",
                answer="?",
                is_correct=True,
                feedback="",
                difficulty=2,
            ))

        assert student.consecutive_correct == 3

        # 答错一题
        student.add_record(QuizRecord(
            point_id="math_g3_001",
            question="?",
            answer="?",
            is_correct=False,
            feedback="",
            difficulty=2,
        ))

        assert student.consecutive_correct == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
