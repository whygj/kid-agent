"""自适应难度调节 - 根据学生表现动态调整出题难度"""

from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass
class DifficultyState:
    """难度状态"""
    current_difficulty: int  # 当前难度 1-5
    recent_correct: int  # 最近答对次数
    recent_wrong: int  # 最近答错次数
    history: deque  # 最近5次答题记录

    def __post_init__(self):
        if self.history is None:
            self.history = deque(maxlen=5)


class AdaptiveDifficulty:
    """自适应难度调节器"""

    def __init__(self, min_difficulty: int = 1, max_difficulty: int = 5):
        """初始化自适应难度调节器

        Args:
            min_difficulty: 最低难度，默认1
            max_difficulty: 最高难度，默认5
        """
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty
        self._student_states: dict[str, DifficultyState] = {}

    def get_difficulty(
        self,
        student_id: str,
        history: list[Any] | None = None,
        default_difficulty: int = 2,
    ) -> int:
        """获取学生当前适合的难度

        Args:
            student_id: 学生ID
            history: 答题历史记录
            default_difficulty: 默认难度

        Returns:
            int: 适合的难度值（1-5）
        """
        state = self._get_state(student_id, default_difficulty)

        # 如果提供了历史记录，更新状态
        if history:
            self._update_from_history(state, history)

        return state.current_difficulty

    def update_after_answer(
        self,
        student_id: str,
        is_correct: bool,
        quiz_difficulty: int | None = None,
    ) -> int:
        """答题后更新难度状态

        Args:
            student_id: 学生ID
            is_correct: 是否答对
            quiz_difficulty: 当前题目的难度（可选）

        Returns:
            int: 更新后的难度值
        """
        state = self._get_state(student_id)

        # 记录答题结果
        state.history.append(is_correct)

        if is_correct:
            state.recent_correct += 1
            state.recent_wrong = 0
        else:
            state.recent_wrong += 1
            state.recent_correct = 0

        # 调整难度
        return self._adjust_difficulty(state, quiz_difficulty)

    def reset_student(self, student_id: str) -> None:
        """重置学生的难度状态

        Args:
            student_id: 学生ID
        """
        if student_id in self._student_states:
            del self._student_states[student_id]

    def get_student_stats(self, student_id: str) -> dict[str, Any]:
        """获取学生的难度统计信息

        Args:
            student_id: 学生ID

        Returns:
            dict: 统计信息
        """
        state = self._get_state(student_id)
        history_list = list(state.history)

        return {
            "current_difficulty": state.current_difficulty,
            "recent_correct": state.recent_correct,
            "recent_wrong": state.recent_wrong,
            "total_history": len(history_list),
            "recent_accuracy": sum(history_list) / len(history_list) if history_list else 0,
        }

    def _get_state(self, student_id: str, default_difficulty: int = 2) -> DifficultyState:
        """获取或创建学生的难度状态

        Args:
            student_id: 学生ID
            default_difficulty: 默认难度

        Returns:
            DifficultyState: 难度状态
        """
        if student_id not in self._student_states:
            self._student_states[student_id] = DifficultyState(
                current_difficulty=default_difficulty,
                recent_correct=0,
                recent_wrong=0,
                history=deque(maxlen=5),
            )
        return self._student_states[student_id]

    def _update_from_history(self, state: DifficultyState, history: list[Any]) -> None:
        """根据历史记录更新状态"""
        # 取最近5条记录
        recent = history[:5]

        # 统计最近的对错（支持简单布尔值和带有 is_correct 属性的对象）
        def get_is_correct(h: Any) -> bool:
            if isinstance(h, bool):
                return h
            return getattr(h, "is_correct", False)

        state.recent_correct = sum(1 for h in recent if get_is_correct(h))
        state.recent_wrong = sum(1 for h in recent if not get_is_correct(h))

        # 更新历史队列
        state.history.clear()
        for h in recent:
            state.history.append(get_is_correct(h))

        # 根据表现调整初始难度
        if state.recent_correct >= 3 and state.recent_wrong == 0:
            state.current_difficulty = min(self.max_difficulty, state.current_difficulty + 1)
        elif state.recent_wrong >= 3 and state.recent_correct == 0:
            state.current_difficulty = max(self.min_difficulty, state.current_difficulty - 1)

    def _adjust_difficulty(
        self,
        state: DifficultyState,
        quiz_difficulty: int | None,
    ) -> int:
        """根据最近表现调整难度

        调整规则：
        - 答对3题以上 -> 难度+1
        - 答错2题以上 -> 难度-1
        - 难度范围 1-5

        Args:
            state: 难度状态
            quiz_difficulty: 当前题目的难度（可选，用于判断是否需要调整）

        Returns:
            int: 调整后的难度值
        """
        # 如果连续答对3题以上，提升难度
        if state.recent_correct >= 3:
            new_difficulty = state.current_difficulty + 1
            state.current_difficulty = min(new_difficulty, self.max_difficulty)
            state.recent_correct = 0  # 重置计数

        # 如果连续答错2题以上，降低难度
        elif state.recent_wrong >= 2:
            new_difficulty = state.current_difficulty - 1
            state.current_difficulty = max(new_difficulty, self.min_difficulty)
            state.recent_wrong = 0  # 重置计数

        return state.current_difficulty


# 默认自适应难度调节器实例
_default_adapter: AdaptiveDifficulty | None = None


def get_adaptive_difficulty() -> AdaptiveDifficulty:
    """获取默认自适应难度调节器实例（懒加载）"""
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = AdaptiveDifficulty()
    return _default_adapter