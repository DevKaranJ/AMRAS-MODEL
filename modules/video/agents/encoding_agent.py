"""Real encoding agent using FFmpeg.

Handles final video encoding with multi-pass, subtitle burn-in, and format conversion.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from modules.video.exceptions import EncodingError
from app.core.logger import get_logger

logger = get_logger("amras.video.encoding")


class EncodingInput(BaseModel):
    input_path: str
    output_path: str
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    video_bitrate: str = "5M"
    audio_bitrate: str = "128k"
    preset: str = "medium"  # ultrafast, fast, medium, slow, veryslow
    crf: int = 23  # 0-51, lower = better quality
    resolution: str = "1920x1080"
    fps: int = 30
    subtitle_path: Optional[str] = None
    subtitle_style: Optional[str] = None


class EncodingOutput(BaseModel):
    output_path: str
    file_size_bytes: int
    duration: float
    success: bool = True


def _find_ffmpeg() -> str:
    """Find FFmpeg executable path."""
    return shutil.which("ffmpeg") or "ffmpeg"


def _find_ffprobe() -> str:
    """Find FFprobe executable path."""
    return shutil.which("ffprobe") or "ffprobe"


def _run_ffmpeg(args: list, timeout: int = 600) -> tuple[bool, str]:
    """Run FFmpeg command."""
    ffmpeg = _find_ffmpeg()
    cmd = [ffmpeg, "-y"] + args

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timed out"
    except FileNotFoundError:
        return False, "FFmpeg not found"


def _get_duration(file_path: str) -> float:
    """Get media file duration using ffprobe."""
    try:
        result = subprocess.run(
            [
                _find_ffprobe(),
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception:
        pass
    return 0.0


class EncodingAgent:
    """Real video encoding agent using FFmpeg."""

    def __init__(self):
        logger.info("encoding_agent_initialized")

    async def execute(self, input_data: EncodingInput) -> EncodingOutput:
        """Encode video with specified settings."""
        try:
            if not os.path.exists(input_data.input_path):
                raise EncodingError(f"Input file not found: {input_data.input_path}")

            # Parse resolution
            width, height = input_data.resolution.split("x")

            # Build encoding arguments
            args = [
                "-i", input_data.input_path,
                "-c:v", input_data.video_codec,
                "-preset", input_data.preset,
                "-crf", str(input_data.crf),
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                "-r", str(input_data.fps),
                "-c:a", input_data.audio_codec,
                "-b:a", input_data.audio_bitrate,
                "-ar", "44100",
                "-pix_fmt", "yuv420p",
            ]

            # Add subtitle burn-in if provided
            if input_data.subtitle_path and os.path.exists(input_data.subtitle_path):
                subtitle_filter = self._build_subtitle_filter(input_data)
                args.extend(["-vf", subtitle_filter])

            args.append(input_data.output_path)

            success, stderr = _run_ffmpeg(args)

            if not success:
                raise EncodingError(f"Encoding failed: {stderr[:300]}")

            # Get output info
            output_size = Path(input_data.output_path).stat().st_size
            duration = _get_duration(input_data.output_path)

            logger.info(
                "video_encoded",
                output=input_data.output_path,
                size_mb=round(output_size / 1024 / 1024, 2),
                duration=duration,
            )

            return EncodingOutput(
                output_path=input_data.output_path,
                file_size_bytes=output_size,
                duration=duration,
            )

        except Exception as e:
            logger.error("encoding_failed", error=str(e))
            raise EncodingError(f"Encoding failed: {e}")

    def _build_subtitle_filter(self, input_data: EncodingInput) -> str:
        """Build FFmpeg subtitle filter string."""
        subtitle_path = input_data.subtitle_path.replace("\\", "/").replace(":", "\\:")

        # Basic subtitle style
        style = (
            "FontName=Arial,"
            "FontSize=24,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "Outline=2,"
            "Shadow=1,"
            "MarginV=30"
        )

        if input_data.subtitle_style:
            style = input_data.subtitle_style

        return f"subtitles='{subtitle_path}':force_style='{style}'"


class TransitionAgent:
    """Real transition agent using FFmpeg xfade filter."""

    TRANSITIONS = {
        "fade": "fade",
        "fadeblack": "fadeblack",
        "fadewhite": "fadewhite",
        "dissolve": "dissolve",
        "wipeleft": "wipeleft",
        "wiperight": "wiperight",
        "wipeup": "wipeup",
        "wipedown": "wipedown",
        "slideleft": "slideleft",
        "slideright": "slideright",
        "slideup": "slideup",
        "slidedown": "slidedown",
        "smoothleft": "smoothleft",
        "smoothright": "smoothright",
    }

    def __init__(self):
        logger.info("transition_agent_initialized")

    def apply_transition(
        self,
        clip1_path: str,
        clip2_path: str,
        output_path: str,
        transition: str = "fade",
        duration: float = 0.5,
    ) -> bool:
        """Apply transition between two video clips."""
        if transition not in self.TRANSITIONS:
            transition = "fade"

        transition_name = self.TRANSITIONS[transition]

        args = [
            "-i", clip1_path,
            "-i", clip2_path,
            "-filter_complex",
            f"[0:v][1:v]xfade=transition={transition_name}:duration={duration}:offset=auto",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-an",
            output_path,
        ]

        success, stderr = _run_ffmpeg(args)
        if success:
            logger.info("transition_applied", transition=transition, output=output_path)
        return success


class AnimationAgent:
    """Real animation agent for Ken Burns effects."""

    def __init__(self):
        logger.info("animation_agent_initialized")

    def generate_camera_path(
        self,
        image_path: str,
        output_path: str,
        duration: float = 5.0,
        effect: str = "zoom_in",
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
    ) -> bool:
        """Generate animated video from still image with Ken Burns effect."""
        from modules.video.agents.scene_renderer import SceneRendererAgent, SceneRendererInput

        renderer = SceneRendererAgent()
        input_data = SceneRendererInput(
            image_path=image_path,
            output_path=output_path,
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            camera_effect=effect,
        )

        try:
            result = renderer.execute(input_data)
            return result.success
        except Exception as e:
            logger.error("animation_failed", error=str(e))
            return False
