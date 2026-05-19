"""学生模型 - 追踪学生状态和掌握程度"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum


class MasteryLevel(IntEnum):
    """掌握程度"""
    UNKNOWN = 0  # 未接触
    EXPOSING = 1  # 接触过
    FUZZY = 2  # 模糊（做题有对有错）
    MASTERED = 3  # 掌握（连续正确）
    FORGOTTEN = 4  # 遗忘（长时间没复习又错了）


@dataclass
class QuizRecord:
    """答题记录"""
    point_id: str
    question: str
    answer: str
    is_correct: bool
    feedback: str
    difficulty: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StudentModel:
    """学生模型"""
    id: str
    name: str
    grade: int
    mastery: dict[str, MasteryLevel] = field(default_factory=dict)
    history: list[QuizRecord] = field(default_factory=list)
    total_xp: int = 0
    streak_days: int = 0
    last_activity: datetime | None = None
    preferences: dict[str, str] = field(default_factory=dict)

    def get_mastery(self, point_id: str) -> MasteryLevel:
        """获取知识点掌握程度"""
        return self.mastery.get(point_id, MasteryLevel.UNKNOWN)

    def update_mastery(
        self,
        point_id: str,
        is_correct: bool,
    ) -> MasteryLevel:
        """更新知识点掌握程度"""
        current = self.mastery.get(point_id, MasteryLevel.UNKNOWN)

        # 获取最近该知识点的答题记录
        recent_records = [
            r for r in self.history[-10:] if r.point_id == point_id
        ]

        # 连续正确次数
        consecutive_correct = 0
        for record in reversed(recent_records):
            if record.is_correct:
                consecutive_correct += 1
            else:
                break

        # 最近n题正确率
        if recent_records:
            recent_accuracy = sum(1 for r in recent_records if r.is_correct) / len(recent_records)
        else:
            recent_accuracy = 1.0 if is_correct else 0.0

        # 更新逻辑
        if current == MasteryLevel.UNKNOWN:
            if is_correct:
                new_level = MasteryLevel.EXPOSING
            else:
                new_level = MasteryLevel.EXPOSING

        elif current == MasteryLevel.EXPOSING:
            if consecutive_correct >= 2:
                new_level = MasteryLevel.FUZZY
            elif recent_accuracy < 0.3:
                new_level = MasteryLevel.FUZZY
            else:
                new_level = current

        elif current == MasteryLevel.FUZZY:
            if consecutive_correct >= 5:
                new_level = MasteryLevel.MASTERED
            elif recent_accuracy < 0.4:
                new_level = MasteryLevel.FUZZY
            else:
                new_level = current

        elif current == MasteryLevel.MASTERED:
            if not is_correct:
                # 检查是否长时间没复习
                last_correct = None
                for record in reversed(self.history):
                    if record.point_id == point_id and record.is_correct:
                        last_correct = record.timestamp
                        break

                if last_correct:
                    days_since = (datetime.now() - last_correct).days
                    if days_since > 7:
                        new_level = MasteryLevel.FORGOTTEN
                    else:
                        new_level = MasteryLevel.FUZZY
                else:
                    new_level = MasteryLevel.FUZZY
            else:
                new_level = current

        else:  # FORGOTTEN
            if consecutive_correct >= 3:
                new_level = MasteryLevel.MASTERED
            else:
                new_level = MasteryLevel.FUZZY

        self.mastery[point_id] = new_level
        return new_level

    def add_record(self, record: QuizRecord) -> None:
        """添加答题记录"""
        self.history.append(record)
        self.last_activity = datetime.now()

        # 更新掌握程度
        self.update_mastery(record.point_id, record.is_correct)

        # 更新经验值
        xp_gain = 10 if record.is_correct else 3
        self.total_xp += xp_gain

    def get_weak_points(self) -> list[str]:
        """获取薄弱知识点列表"""
        weak = []
        for point_id, level in self.mastery.items():
            if level in (MasteryLevel.FUZZY, MasteryLevel.FORGOTTEN):
                weak.append(point_id)
        return weak

    def get_mastered_points(self) -> list[str]:
        """获取已掌握的知识点列表"""
        return [
            point_id
            for point_id, level in self.mastery.items()
            if level == MasteryLevel.MASTERED
        ]

    def get_accuracy(self, point_id: str | None = None) -> float:
        """获取正确率"""
        records = self.history if point_id is None else [
            r for r in self.history if r.point_id == point_id
        ]

        if not records:
            return 0.0

        return sum(1 for r in records if r.is_correct) / len(records)

    def to_dict(self) -> dict:
        """导出为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "grade": self.grade,
            "mastery": {pid: level.value for pid, level in self.mastery.items()},
            "total_xp": self.total_xp,
            "streak_days": self.streak_days,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }