"""测试自适应难度调节"""

import pytest
from collections import deque

from src.engine.adaptive import AdaptiveDifficulty, DifficultyState


class TestDifficultyState:
    """测试难度状态"""

    def test_difficulty_state_creation(self):
        """测试难度状态创建"""
        state = DifficultyState(
            current_difficulty=2,
            recent_correct=3,
            recent_wrong=1,
            history=deque([True, True, True, False], maxlen=5),
        )

        assert state.current_difficulty == 2
        assert state.recent_correct == 3
        assert state.recent_wrong == 1
        assert len(state.history) == 4

    def test_difficulty_state_default_history(self):
        """测试难度状态默认历史队列"""
        state = DifficultyState(
            current_difficulty=2,
            recent_correct=0,
            recent_wrong=0,
            history=None,
        )

        assert state.history is not None
        assert state.history.maxlen == 5
        assert len(state.history) == 0


class TestAdaptiveDifficulty:
    """测试自适应难度调节器"""

    @pytest.fixture
    def adapter(self):
        """创建测试用适配器"""
        return AdaptiveDifficulty(min_difficulty=1, max_difficulty=5)

    def test_adapter_initialization(self, adapter):
        """测试适配器初始化"""
        assert adapter.min_difficulty == 1
        assert adapter.max_difficulty == 5
        assert len(adapter._student_states) == 0

    def test_get_difficulty_default(self, adapter):
        """测试获取默认难度"""
        difficulty = adapter.get_difficulty("student_1")
        assert difficulty == 2  # 默认难度

    def test_get_difficulty_with_custom_default(self, adapter):
        """测试获取自定义默认难度"""
        difficulty = adapter.get_difficulty("student_1", default_difficulty=3)
        assert difficulty == 3

    def test_get_difficulty_from_history(self, adapter):
        """测试从历史记录获取难度"""
        history = [True, True, True]  # 连对3题
        difficulty = adapter.get_difficulty("student_1", history=history)
        assert difficulty == 3  # 应该提升难度

    def test_get_difficulty_from_wrong_history(self, adapter):
        """测试从错误历史记录获取难度"""
        history = [False, False, False]  # 连错3题
        difficulty = adapter.get_difficulty("student_1", history=history, default_difficulty=3)
        assert difficulty == 2  # 应该降低难度

    def test_update_after_correct_answer(self, adapter):
        """测试答对后更新难度"""
        adapter._student_states["student_1"] = DifficultyState(
            current_difficulty=2,
            recent_correct=2,
            recent_wrong=0,
            history=deque(maxlen=5),
        )

        new_difficulty = adapter.update_after_answer("student_1", True)
        assert new_difficulty == 3  # 连对3题，难度+1
        assert adapter._student_states["student_1"].recent_correct == 0  # 应重置

    def test_update_after_wrong_answer(self, adapter):
        """测试答错后更新难度"""
        adapter._student_states["student_1"] = DifficultyState(
            current_difficulty=3,
            recent_correct=0,
            recent_wrong=1,
            history=deque(maxlen=5),
        )

        new_difficulty = adapter.update_after_answer("student_1", False)
        assert new_difficulty == 2  # 连错2题，难度-1
        assert adapter._student_states["student_1"].recent_wrong == 0  # 应重置

    def test_difficulty_upper_bound(self, adapter):
        """测试难度上限"""
        adapter._student_states["student_1"] = DifficultyState(
            current_difficulty=5,  # 已经是最高难度
            recent_correct=2,
            recent_wrong=0,
            history=deque(maxlen=5),
        )

        new_difficulty = adapter.update_after_answer("student_1", True)
        assert new_difficulty == 5  # 不应超过5

    def test_difficulty_lower_bound(self, adapter):
        """测试难度下限"""
        adapter._student_states["student_1"] = DifficultyState(
            current_difficulty=1,  # 已经是最低难度
            recent_correct=0,
            recent_wrong=1,
            history=deque(maxlen=5),
        )

        new_difficulty = adapter.update_after_answer("student_1", False)
        assert new_difficulty == 1  # 不应低于1

    def test_consecutive_correct_increases_difficulty(self, adapter):
        """测试连续答对增加难度"""
        difficulty = adapter.update_after_answer("student_1", True)
        assert difficulty == 2

        difficulty = adapter.update_after_answer("student_1", True)
        assert difficulty == 2

        difficulty = adapter.update_after_answer("student_1", True)
        assert difficulty == 3  # 第3次答对后难度提升

    def test_consecutive_wrong_decreases_difficulty(self, adapter):
        """测试连续答错降低难度"""
        adapter._student_states["student_1"] = DifficultyState(
            current_difficulty=3,
            recent_correct=0,
            recent_wrong=0,
            history=deque(maxlen=5),
        )

        difficulty = adapter.update_after_answer("student_1", False)
        assert difficulty == 3

        difficulty = adapter.update_after_answer("student_1", False)
        assert difficulty == 2  # 第2次答错后难度降低

    def test_reset_student(self, adapter):
        """测试重置学生状态"""
        adapter._student_states["student_1"] = DifficultyState(
            current_difficulty=3,
            recent_correct=5,
            recent_wrong=2,
            history=deque([True, True, False], maxlen=5),
        )

        adapter.reset_student("student_1")
        assert "student_1" not in adapter._student_states

    def test_reset_nonexistent_student(self, adapter):
        """测试重置不存在的学生"""
        # 不应抛出异常
        adapter.reset_student("nonexistent")

    def test_get_student_stats(self, adapter):
        """测试获取学生统计信息"""
        adapter._student_states["student_1"] = DifficultyState(
            current_difficulty=3,
            recent_correct=3,
            recent_wrong=1,
            history=deque([True, True, True, False], maxlen=5),
        )

        stats = adapter.get_student_stats("student_1")

        assert stats["current_difficulty"] == 3
        assert stats["recent_correct"] == 3
        assert stats["recent_wrong"] == 1
        assert stats["total_history"] == 4
        assert stats["recent_accuracy"] == 0.75

    def test_get_student_stats_empty(self, adapter):
        """测试获取空统计信息"""
        stats = adapter.get_student_stats("new_student")

        assert stats["current_difficulty"] == 2  # 默认难度
        assert stats["recent_correct"] == 0
        assert stats["recent_wrong"] == 0
        assert stats["total_history"] == 0
        assert stats["recent_accuracy"] == 0.0

    def test_new_student_default_difficulty(self, adapter):
        """测试新学生默认难度"""
        difficulty = adapter.get_difficulty("new_student")
        assert difficulty == 2

    def test_new_student_custom_default(self, adapter):
        """测试新学生自定义默认难度"""
        adapter = AdaptiveDifficulty(min_difficulty=1, max_difficulty=5)
        difficulty = adapter.get_difficulty("new_student", default_difficulty=4)
        assert difficulty == 4

    def test_custom_bounds(self):
        """测试自定义边界"""
        adapter = AdaptiveDifficulty(min_difficulty=2, max_difficulty=4)

        # 尝试超出上界
        adapter._student_states["s1"] = DifficultyState(
            current_difficulty=4,
            recent_correct=2,
            recent_wrong=0,
            history=deque(maxlen=5),
        )
        new_difficulty = adapter.update_after_answer("s1", True)
        assert new_difficulty == 4

        # 尝试超出下界
        adapter._student_states["s2"] = DifficultyState(
            current_difficulty=2,
            recent_correct=0,
            recent_wrong=1,
            history=deque(maxlen=5),
        )
        new_difficulty = adapter.update_after_answer("s2", False)
        assert new_difficulty == 2

    def test_multiple_students_independent(self, adapter):
        """测试多个学生状态独立"""
        # 学生1连续答对
        for _ in range(3):
            adapter.update_after_answer("student_1", True)

        # 学生2连续答错
        for _ in range(2):
            adapter.update_after_answer("student_2", False)

        stats1 = adapter.get_student_stats("student_1")
        stats2 = adapter.get_student_stats("student_2")

        assert stats1["current_difficulty"] == 3
        assert stats2["current_difficulty"] == 1

    def test_difficulty_stability(self, adapter):
        """测试难度稳定性（交替正确和错误）"""
        # 交替正确和错误
        for i in range(10):
            adapter.update_after_answer("student_1", i % 2 == 0)

        difficulty = adapter.get_difficulty("student_1")
        # 应该保持在默认难度附近
        assert difficulty in (1, 2, 3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
