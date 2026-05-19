"""会话管理 - 管理学习会话状态"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from src.memory.student import QuizRecord


class SessionState(Enum):
    """会话状态"""
    IDLE = "idle"  # 空闲
    QUIZ = "quiz"  # 做题中
    EXPLAIN = "explain"  # 讲解中
    DIAGNOSE = "diagnose"  # 诊断中


class MessageType(Enum):
    """消息类型"""
    CHAT = "chat"  # 闲聊
    ANSWER = "answer"  # 答题
    QUESTION = "question"  # 提问
    HELP = "help"  # 求助
    COMMAND = "command"  # 命令


@dataclass
class Message:
    """消息"""
    role: str  # user/assistant
    content: str
    message_type: MessageType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """学习会话"""
    student_id: str
    state: SessionState = SessionState.IDLE
    current_quiz: Any = None  # 当前题目
    messages: list[Message] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str, message_type: MessageType) -> None:
        """添加消息"""
        self.messages.append(
            Message(
                role=role,
                content=content,
                message_type=message_type,
            )
        )
        self.last_active = datetime.now()

    def set_state(self, state: SessionState) -> None:
        """设置会话状态"""
        self.state = state
        self.last_active = datetime.now()

    def get_recent_messages(self, limit: int = 10) -> list[Message]:
        """获取最近消息"""
        return self.messages[-limit:]

    def is_idle(self, timeout_minutes: int = 5) -> bool:
        """检查是否空闲超时"""
        if self.state == SessionState.IDLE:
            return True

        elapsed = (datetime.now() - self.last_active).total_seconds() / 60
        return elapsed > timeout_minutes


class SessionManager:
    """会话管理器"""

    def __init__(self):
        """初始化会话管理器"""
        self._sessions: dict[str, Session] = {}

    def create_session(self, student_id: str) -> Session:
        """创建新会话"""
        session = Session(student_id=student_id)
        self._sessions[student_id] = session
        return session

    def get_session(self, student_id: str) -> Session | None:
        """获取会话"""
        return self._sessions.get(student_id)

    def close_session(self, student_id: str) -> None:
        """关闭会话"""
        if student_id in self._sessions:
            del self._sessions[student_id]

    def cleanup_idle_sessions(self, timeout_minutes: int = 30) -> list[str]:
        """清理空闲会话"""
        to_remove = [
            student_id
            for student_id, session in self._sessions.items()
            if session.is_idle(timeout_minutes)
        ]
        for student_id in to_remove:
            del self._sessions[student_id]
        return to_remove


# 默认会话管理器实例
_default_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """获取默认会话管理器实例（懒加载）"""
    global _default_manager
    if _default_manager is None:
        _default_manager = SessionManager()
    return _default_manager