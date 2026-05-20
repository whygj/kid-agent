"""数学视频生成引擎（儿童版）"""

import asyncio
import re
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List

from .models import VideoTask, MathVideoConfig, VideoGenerationResult, VideoTaskStatus


class MathVideoEngine:
    """数学概念讲解视频生成引擎

    使用 Manim 生成数学可视化，配合 TTS 生成儿童友好的讲解视频。
    """

    def __init__(self, config: Optional[MathVideoConfig] = None):
        self.config = config or MathVideoConfig()
        self._manim_available = self._check_manim()

    def _check_manim(self) -> bool:
        """检查 Manim 是否可用"""
        try:
            result = subprocess.run(
                ["manim", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def generate(self, task: VideoTask) -> VideoGenerationResult:
        """生成数学讲解视频

        Args:
            task: 视频任务

        Returns:
            VideoGenerationResult: 生成结果
        """
        if not self._manim_available:
            return VideoGenerationResult(
                task_id=task.id,
                status=VideoTaskStatus.FAILED,
                progress=0,
                video_url="",
                error_message="Manim 未安装，无法生成视频"
            )

        task.status = VideoTaskStatus.GENERATING
        task.started_at = None

        try:
            # 1. 生成 Manim 脚本
            script_path = await self._generate_manim_script(task)
            task.update_progress(20)

            # 2. 生成 TTS 音频
            audio_path = await self._generate_audio(task)
            task.update_progress(50)

            # 3. 合成视频
            video_path = await self._render_video(task, script_path, audio_path)
            task.update_progress(90)

            # 4. 清理临时文件
            await self._cleanup_temp_files(script_path, audio_path)

            task.status = VideoTaskStatus.DONE
            task.video_path = str(video_path)
            task.update_progress(100)

            return VideoGenerationResult(
                task_id=task.id,
                status=VideoTaskStatus.DONE,
                progress=100,
                video_url=f"/videos/{Path(video_path).name}",
                error_message=""
            )

        except Exception as e:
            task.status = VideoTaskStatus.FAILED
            task.error_message = str(e)
            return VideoGenerationResult(
                task_id=task.id,
                status=VideoTaskStatus.FAILED,
                progress=task.progress,
                video_url="",
                error_message=str(e)
            )

    async def _generate_manim_script(self, task: VideoTask) -> Path:
        """生成 Manim Python 脚本"""
        colors = self.config.COLORS

        script_content = f'''from manim import *
import numpy as np

class {self._sanitize_scene_name(task.concept_name)}(Scene):
    def construct(self):
        # 配置
        BG_COLOR = "{colors["BG"]}"
        PRIMARY_COLOR = "{colors["PRIMARY"]}"
        SECONDARY_COLOR = "{colors["SECONDARY"]}"
        TEXT_COLOR = "{colors["TEXT"]}"
        ACCENT_COLOR = "{colors["ACCENT"]}"

        self.camera.background_color = BG_COLOR

        # 标题场景
        title = Text("{task.concept_name}", font_size=72, color=PRIMARY_COLOR)
        subtitle = Text("小学生数学讲解", font_size=36, color=TEXT_COLOR)
        subtitle.next_to(title, DOWN, buff=0.5)

        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=1)

        # 概念描述
        description = Text("{task.description[:50] if task.description else ''}",
                          font_size=36, color=TEXT_COLOR, line_spacing=1.2)
        description.scale_to_fit_width(self.camera.frame_width * 0.9)
        self.play(Write(description), run_time=3)
        self.wait(2)
        self.play(FadeOut(description), run_time=1)

        # 示例演示
        {self._generate_example_scenes(task.examples[:3], colors)}

        # 总结
        summary = Text("记住了吗？继续加油！", font_size=48, color=ACCENT_COLOR)
        self.play(FadeIn(summary), run_time=1)
        self.wait(2)
        self.play(FadeOut(summary), run_time=1)

        self.wait(1)

    {self._generate_example_methods(task.examples[:3], colors)}
'''

        temp_dir = Path(tempfile.gettempdir()) / "kid-agent" / "manim"
        temp_dir.mkdir(parents=True, exist_ok=True)
        script_path = temp_dir / f"{task.id}_scene.py"

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return script_path

    def _sanitize_scene_name(self, name: str) -> str:
        """清理场景名称使其符合 Python 类命名规则"""
        # 移除特殊字符，保留字母数字和下划线
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # 确保以字母开头
        if sanitized and sanitized[0].isdigit():
            sanitized = f"Scene_{sanitized}"
        return sanitized or "MathScene"

    def _generate_example_scenes(self, examples: List[str], colors: dict) -> str:
        """生成示例场景代码"""
        if not examples:
            return 'pass'

        scenes = []
        for i, example in enumerate(examples, 1):
            scenes.append(f'''
        # 示例 {i}
        example_text = Text("{example[:60]}...", font_size=32, color="{colors["TEXT"]}")
        example_text.scale_to_fit_width(self.camera.frame_width * 0.85)
        self.play(Write(example_text), run_time=2)
        self.wait(2)
        self.play(FadeOut(example_text), run_time=1)
''')
        return "\n".join(scenes)

    def _generate_example_methods(self, examples: List[str], colors: dict) -> str:
        """生成示例方法（如果有复杂动画）"""
        return "# 预留给复杂动画方法"

    async def _generate_audio(self, task: VideoTask) -> Optional[Path]:
        """生成 TTS 音频

        简化版：返回 None，让 Manim 使用静默视频
        """
        # 实际项目可以集成 edge-tts 或其他 TTS
        return None

    async def _render_video(
        self,
        task: VideoTask,
        script_path: Path,
        audio_path: Optional[Path]
    ) -> Path:
        """渲染视频"""
        output_dir = Path(tempfile.gettempdir()) / "kid-agent" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{task.id}.mp4"

        # 运行 Manim
        cmd = [
            "manim",
            str(script_path),
            self._sanitize_scene_name(task.concept_name),
            "-ql",  # 低质量，快速渲染
            "-o", str(output_path),
            "--format", self.config.OUTPUT_FORMAT,
            "--fps", str(self.config.FPS),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Manim 渲染失败: {stderr.decode()}")

        return output_path

    async def _cleanup_temp_files(self, *paths: Optional[Path]):
        """清理临时文件"""
        for path in paths:
            if path and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass

    def is_available(self) -> bool:
        """检查视频生成是否可用"""
        return self._manim_available

    async def estimate_duration(self, task: VideoTask) -> int:
        """估算视频时长（秒）"""
        # 基于示例数量和描述长度估算
        example_time = len(task.examples) * 10  # 每个示例10秒
        desc_time = len(task.description) // 10  # 描述文本每10个字符1秒
        base_time = 20  # 片头片尾
        return min(base_time + example_time + desc_time, task.duration_target)


__all__ = ["MathVideoEngine"]