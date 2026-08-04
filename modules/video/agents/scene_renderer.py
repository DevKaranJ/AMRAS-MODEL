"""Real scene renderer using FFmpeg.

Renders individual scenes with Ken Burns effects, transitions, and audio overlay.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from modules.video.exceptions import SceneRenderError
from app.core.logger import get_logger

logger = get_logger("amras.video.scene_renderer")


class SceneRendererInput(BaseModel):
    image_path: str
    audio_path: Optional[str] = None
    output_path: str
    duration: float = 5.0
    width: int = 1920
    height: int = 1080
    fps: int = 30
    camera_effect: str = "zoom_in"  # zoom_in, zoom_out, pan_left, pan_right, static
    effect_strength: float = 0.1  # 0.0-1.0


class SceneRendererOutput(BaseModel):
    output_path: str
    duration: float
    width: int
    height: int
    success: bool = True


def _find_ffmpeg() -> str:
    """Find FFmpeg executable path."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    # Check common Windows install locations
    import os
    for candidate in [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    ]:
        if os.path.exists(candidate):
            return candidate
    return "ffmpeg"


def _run_ffmpeg(args: list, timeout: int = 300) -> tuple[bool, str]:
    """Run FFmpeg command and return (success, stderr)."""
    ffmpeg = _find_ffmpeg()
    cmd = [ffmpeg, "-y"] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timed out"
    except FileNotFoundError:
        return False, "FFmpeg not found"


class SceneRendererAgent:
    """Real scene renderer using FFmpeg zoompan filter."""

    def __init__(self):
        logger.info("scene_renderer_initialized")

    async def execute(self, input_data: SceneRendererInput) -> SceneRendererOutput:
        """Render a single scene from an image with Ken Burns effect."""
        try:
            if not os.path.exists(input_data.image_path):
                raise SceneRenderError(f"Image not found: {input_data.image_path}")

            # Build FFmpeg filter based on camera effect
            filter_complex = self._build_zoompan_filter(input_data)

            # Build FFmpeg arguments
            args = [
                "-loop", "1",
                "-i", input_data.image_path,
            ]

            if input_data.audio_path and os.path.exists(input_data.audio_path):
                args.extend(["-i", input_data.audio_path])

            args.extend([
                "-filter_complex", filter_complex,
                "-t", str(input_data.duration),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
            ])

            if input_data.audio_path and os.path.exists(input_data.audio_path):
                args.extend(["-c:a", "aac", "-b:a", "128k"])
            else:
                args.extend(["-an"])

            args.append(input_data.output_path)

            success, stderr = _run_ffmpeg(args)

            if not success:
                raise SceneRenderError(f"FFmpeg failed: {stderr[:200]}")

            logger.info(
                "scene_rendered",
                output=input_data.output_path,
                duration=input_data.duration,
                effect=input_data.camera_effect,
            )

            return SceneRendererOutput(
                output_path=input_data.output_path,
                duration=input_data.duration,
                width=input_data.width,
                height=input_data.height,
            )

        except Exception as e:
            logger.error("scene_render_failed", error=str(e))
            raise SceneRenderError(f"Scene render failed: {e}")

    def _build_zoompan_filter(self, input_data: SceneRendererInput) -> str:
        """Build FFmpeg zoompan filter based on camera effect."""
        w, h = input_data.width, input_data.height
        fps = input_data.fps
        duration_frames = int(input_data.duration * fps)
        strength = input_data.effect_strength

        if input_data.camera_effect == "zoom_in":
            # Zoom in slowly to center
            return (
                f"zoompan=z='min(zoom+{strength * 0.001},1.5)':"
                f"d={duration_frames}:"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"s={w}x{h}:fps={fps}"
            )
        elif input_data.camera_effect == "zoom_out":
            # Zoom out slowly
            return (
                f"zoompan=z='if(eq(on,1),1.5,max(zoom-{strength * 0.001},1.0))':"
                f"d={duration_frames}:"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"s={w}x{h}:fps={fps}"
            )
        elif input_data.camera_effect == "pan_left":
            # Pan from right to left
            return (
                f"zoompan=z=1.2:"
                f"d={duration_frames}:"
                f"x='iw/2-(iw/zoom/2)-on*{strength * 2}':"
                f"y='ih/2-(ih/zoom/2)':"
                f"s={w}x{h}:fps={fps}"
            )
        elif input_data.camera_effect == "pan_right":
            # Pan from left to right
            return (
                f"zoompan=z=1.2:"
                f"d={duration_frames}:"
                f"x='iw/2-(iw/zoom/2)+on*{strength * 2}':"
                f"y='ih/2-(ih/zoom/2)':"
                f"s={w}x{h}:fps={fps}"
            )
        else:
            # Static - no zoom
            return (
                f"zoompan=z=1:"
                f"d={duration_frames}:"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"s={w}x{h}:fps={fps}"
            )
