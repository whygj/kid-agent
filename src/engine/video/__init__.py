"""视频生成引擎

支持数学概念讲解（Manim+TTS）和词汇视频（Remotion）。
"""

from .models import VideoTask, VideoTaskStatus, VideoType
from .selector import VideoSelector, VideoSelection
from .math_video import MathVideoEngine

__all__ = [
    "VideoSelector",
    "VideoType",
    "VideoTask",
    "VideoTaskStatus",
    "MathVideoEngine",
    "VideoSelection",
]