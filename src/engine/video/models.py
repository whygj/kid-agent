"""视频生成数据模型"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional


class VideoType(str, Enum):
    """视频类型"""
    MATH = "math"           # 数学概念讲解（Manim+TTS）
    VOCAB = "vocab"         # 英语词汇视频（Remotion）


class VideoTaskStatus(str, Enum):
    """视频任务状态"""
    QUEUED = "queued"       # 排队中
    GENERATING = "generating"  # 生成中
    DONE = "done"           # 完成
    FAILED = "failed"        # 失败


@dataclass
class VideoTask:
    """视频生成任务"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str = ""
    point_id: str = ""
    video_type: VideoType = VideoType.MATH
    status: VideoTaskStatus = VideoTaskStatus.QUEUED
    progress: int = 0
    video_path: str = ""
    video_url: str = ""
    error_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 任务参数
    concept_name: str = ""
    description: str = ""
    grade: int = 3
    examples: list[str] = field(default_factory=list)
    common_mistakes: list[str] = field(default_factory=list)

    # 生成配置
    resolution: str = "1920x1080"
    fps: int = 60
    duration_target: int = 180  # 目标3分钟

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "point_id": self.point_id,
            "video_type": self.video_type.value,
            "status": self.status.value,
            "progress": self.progress,
            "video_url": self.video_url,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_time": self._estimate_time(),
        }

    def _estimate_time(self) -> str:
        """估算剩余时间"""
        if self.status == VideoTaskStatus.DONE:
            return "已完成"
        if self.status == VideoTaskStatus.FAILED:
            return "失败"
        if self.progress >= 100:
            return "即将完成"
        if self.status == VideoTaskStatus.QUEUED:
            return "2-5分钟"
        remaining_pct = 100 - self.progress
        remaining_seconds = int(remaining_pct * 1.5)
        return f"{remaining_seconds}秒"

    def update_progress(self, progress: int) -> None:
        """更新进度"""
        self.progress = min(max(progress, 0), 100)
        if progress > 0 and self.started_at is None:
            self.started_at = datetime.now()
        if progress >= 100 and self.completed_at is None:
            self.completed_at = datetime.now()
            self.status = VideoTaskStatus.DONE


@dataclass
class MathVideoConfig:
    """数学视频配置（儿童版）"""
    COLORS: dict = field(default_factory=lambda: {
        "BG": "#0D1117",
        "PRIMARY": "#FF6B6B",
        "SECONDARY": "#4ECDC4",
        "TEXT": "#F0F6FC",
        "ACCENT": "#FFE66D",
        "GRID": "#30363D",
    })

    TIMING: dict = field(default_factory=lambda: {
        "wait_multiplier": 1.3,
        "max_scene_duration": 15,
        "total_video_target": 180,
    })

    RESOLUTION: str = "1920x1080"
    FPS: int = 60
    OUTPUT_FORMAT: str = "mp4"
    AUDIO_CODEC: str = "aac"
    VIDEO_CODEC: str = "libx264"

    SCENE_DURATION: dict = field(default_factory=lambda: {
        "title": 5,
        "hook": 10,
        "concept": 30,
        "example": 25,
        "mistake": 15,
        "practice": 15,
        "summary": 10,
    })


@dataclass
class VideoGenerationResult:
    """视频生成结果"""
    task_id: str
    status: VideoTaskStatus
    progress: int
    video_url: str
    error_message: str = ""