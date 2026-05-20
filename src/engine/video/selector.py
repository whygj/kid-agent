"""视频框架选择器

根据知识点类型自动选择合适的视频生成框架。
"""

from dataclasses import dataclass
from typing import Optional

from src.knowledge.loader import KnowledgePoint


@dataclass
class VideoSelection:
    """视频选择结果"""
    video_type: str  # "math" | "vocab" | "none"
    framework: str  # "manim" | "remotion"
    reason: str
    confidence: float  # 0-1


class VideoSelector:
    """视频框架选择器"""

    MATH_KEYWORDS = [
        "函数", "方程", "不等式", "几何", "图形", "图像", "坐标",
        "证明", "推导", "变换", "映射", "集合", "向量", "矩阵",
        "运算", "加", "减", "乘", "除", "幂", "根", "对数", "三角",
        "圆", "直线", "角度", "距离", "面积", "体积", "公式",
    ]

    VOCAB_KEYWORDS = [
        "英语", "English", "单词", "word", "vocabulary", "词汇",
        "verb", "noun", "adjective", "preposition", "pronunciation",
    ]

    VISUAL_FOCUSED_CATEGORIES = [
        "几何", "函数", "图像", "坐标", "证明", "变换",
    ]

    def select(self, point: KnowledgePoint) -> VideoSelection:
        """根据知识点选择视频类型和框架

        Args:
            point: 知识点对象

        Returns:
            VideoSelection: 选择结果
        """
        # 检查关键词
        name_lower = point.name.lower()
        desc_lower = point.description.lower() if point.description else ""

        # 检查是否适合数学可视化（几何、函数等）
        is_visual_math = any(
            keyword in name_lower or keyword in desc_lower
            for keyword in self.VISUAL_FOCUSED_CATEGORIES
        )

        # 优先判断：数学可视化内容 → Manim
        if point.subject == "数学" and is_visual_math:
            return VideoSelection(
                video_type="math",
                framework="manim",
                reason=f"数学可视化知识点: {point.name}",
                confidence=0.9,
            )

        # 其次：数学一般内容 → Manim+TTS
        if point.subject == "数学":
            return VideoSelection(
                video_type="math",
                framework="manim",
                reason=f"数学知识点: {point.name}",
                confidence=0.7,
            )

        # 英语词汇 → Remotion
        if point.subject == "英语":
            return VideoSelection(
                video_type="vocab",
                framework="remotion",
                reason=f"英语词汇知识点: {point.name}",
                confidence=0.8,
            )

        # 其他情况暂不支持
        return VideoSelection(
            video_type="none",
            framework="none",
            reason=f"暂不支持此类型知识点: {point.subject} - {point.name}",
            confidence=0.0,
        )

    def is_visual_focused(self, name: str, description: str) -> bool:
        """判断是否是可视化友好的知识点"""
        combined = name + " " + description
        return any(keyword in combined for keyword in self.MATH_KEYWORDS)


def is_visual_focused(name: str, description: str) -> bool:
    """判断是否是可视化友好的知识点（辅助函数）"""
    combined = name + " " + (description or "")
    return any(kw in combined for kw in VideoSelector.MATH_KEYWORDS)


__all__ = [
    "VideoSelector",
    "VideoSelection",
    "is_visual_focused",
]