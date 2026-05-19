"""Pydantic models for Web API"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class SessionStartRequest(BaseModel):
    """开始会话请求"""
    student_id: str = Field(..., description="学生ID")


class SessionStartResponse(BaseModel):
    """开始会话响应"""
    greeting: str = Field(..., description="欢迎消息")
    student_id: str = Field(..., description="学生ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class ChatRequest(BaseModel):
    """聊天请求"""
    student_id: str = Field(..., description="学生ID")
    message: str = Field(..., description="用户消息")


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="AI回复")
    intent: str = Field(default="chat", description="识别的意图")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class StudentStatus(BaseModel):
    """学生状态"""
    student_id: str
    name: str
    grade: int
    level: int
    total_xp: int
    streak_days: int
    mastery_count: int = Field(default=0, description="已掌握知识点数")
    fuzzy_count: int = Field(default=0, description="模糊知识点数")


class KnowledgePointMastery(BaseModel):
    """知识点掌握度"""
    point_id: str
    point_name: str
    mastery_level: int
    mastery_name: str


class LearningReport(BaseModel):
    """学习报告"""
    student_id: str
    name: str
    grade: int
    level: int
    total_xp: int
    streak_days: int
    total_quizzes: int
    correct_rate: float
    mastered_points: list[KnowledgePointMastery]
    weak_points: list[KnowledgePointMastery]
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str = "2.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)


class TTSRequest(BaseModel):
    """文字转语音请求"""
    text: str = Field(..., description="要转换为语音的文本")
    voice: str = Field(default="female", description="语音类型")


class WSMessage(BaseModel):
    """WebSocket消息"""
    type: str = Field(..., description="消息类型: message|status|report|error")
    content: str = Field(default="", description="消息内容")
    data: dict[str, Any] = Field(default_factory=dict, description="额外数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")