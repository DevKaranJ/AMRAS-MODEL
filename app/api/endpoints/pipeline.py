"""Full manga-to-video pipeline endpoint.

Orchestrates the complete workflow:
1. Import manga (if not already imported)
2. Vision analysis (panel detection) — local OpenCV
3. OCR (text extraction) — local
4. Story analysis (LLM) — 1 consolidated call
5. Narration script (LLM) — 1 consolidated call
6. Voice generation (Edge TTS) — free, no API
7. Timeline composition — local
8. Video rendering (FFmpeg) — local
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.logger import get_logger
from app.database.session import get_db_session
from app.models.manga import Manga, Page
from modules.story.engine import StoryEngine
from modules.narration.engine import NarrationEngine
from modules.voice.agents import VoiceGenerationAgent, EmotionAgent, AudioStitchingAgent, AudioCleanupAgent
from modules.vision.agents.vision_agent import VisionAgent, LayoutAgent, SceneAnalysisAgent
from modules.vision.preprocessing import preprocess_pipeline
from modules.timeline.agents.scene_composition import SceneCompositionAgent
from modules.video.agents.scene_renderer import SceneRendererAgent, SceneRendererInput
from modules.video.agents.encoding_agent import EncodingAgent, EncodingInput
from modules.video.agents.render_manager import RenderManagerAgent, RenderManagerInput

logger = get_logger("amras.api.pipeline")

router = APIRouter()


class PipelineRunRequest(BaseModel):
    """Request to run the full manga-to-video pipeline."""

    manga_id: int
    chapter_id: Optional[int] = None
    output_dir: str = Field(default="./storage/videos")
    voice: str = Field(default="en-US-GuyNeural")
    style: str = Field(default="narration")
    resolution: str = Field(default="1920x1080")
    fps: int = Field(default=30)
    max_pages: int = Field(default=50, description="Max pages to process (limits API usage)")


class PipelineStatus(BaseModel):
    """Pipeline execution status."""

    job_id: int
    status: str
    current_step: str
    progress: float
    message: str
    output_path: Optional[str] = None
    error: Optional[str] = None


# Global pipeline status tracking
pipeline_jobs: Dict[int, PipelineStatus] = {}


async def _run_full_pipeline(
    job_id: int,
    manga_id: int,
    chapter_id: Optional[int],
    output_dir: str,
    voice: str,
    style: str,
    resolution: str,
    fps: int,
    max_pages: int = 50,
) -> None:
    """Execute the full manga-to-video pipeline in background."""
    from app.database.session import async_session_maker

    try:
        # Ensure AI providers are registered
        from app.shared.providers.base import ensure_providers_registered
        ensure_providers_registered()

        pipeline_jobs[job_id] = PipelineStatus(
            job_id=job_id,
            status="running",
            current_step="initializing",
            progress=0.0,
            message="Starting pipeline...",
        )

        async with async_session_maker() as session:
            # Step 1: Get manga data
            pipeline_jobs[job_id].current_step = "loading_manga"
            pipeline_jobs[job_id].progress = 5.0
            pipeline_jobs[job_id].message = "Loading manga data..."

            stmt = select(Manga).where(Manga.id == manga_id)
            result = await session.execute(stmt)
            manga = result.scalar_one_or_none()

            if not manga:
                raise ValueError(f"Manga {manga_id} not found")

            # Get chapters for this manga
            from app.models.manga import Chapter
            chapter_stmt = select(Chapter).where(Chapter.manga_id == manga_id)
            if chapter_id:
                chapter_stmt = chapter_stmt.where(Chapter.id == chapter_id)
            chapter_result = await session.execute(chapter_stmt)
            chapters = chapter_result.scalars().all()

            if not chapters:
                raise ValueError(f"No chapters found for manga {manga_id}")

            # Get pages from chapters
            chapter_ids = [c.id for c in chapters]
            page_stmt = select(Page).where(Page.chapter_id.in_(chapter_ids)).order_by(Page.page_number)
            page_result = await session.execute(page_stmt)
            all_pages = page_result.scalars().all()

            if not all_pages:
                raise ValueError(f"No pages found for manga {manga_id}")

            # Limit pages for API budget
            pages = all_pages[:max_pages]
            if len(all_pages) > max_pages:
                logger.info("pages_limited", total=len(all_pages), using=len(pages))

            # Step 2: Vision analysis
            pipeline_jobs[job_id].current_step = "vision_analysis"
            pipeline_jobs[job_id].progress = 15.0
            pipeline_jobs[job_id].message = f"Analyzing {len(pages)} pages..."

            vision_agent = VisionAgent()
            layout_agent = LayoutAgent()
            scene_agent = SceneAnalysisAgent()

            all_panels = []
            for i, page in enumerate(pages):
                # Use actual image path from page
                image_path = page.image_path

                if image_path and os.path.exists(image_path):
                    # Run local vision analysis
                    try:
                        vision_result = await vision_agent.execute({
                            "page_id": page.id,
                            "image_path": image_path,
                        })
                        panels = vision_result.get("panels", [])
                        # Add image_path to each panel for video rendering
                        for p in panels:
                            p["image_path"] = image_path
                        # If no panels detected, use the entire page as one panel
                        if not panels:
                            panels = [{
                                "page_id": page.id,
                                "panel_id": 1,
                                "bounding_box": {"x": 0, "y": 0, "w": 1920, "h": 1080},
                                "scene_type": "normal",
                                "speech_bubbles": [],
                                "image_path": image_path,
                            }]
                        all_panels.extend(panels)
                    except Exception as e:
                        logger.warning("vision_failed", page_id=page.id, error=str(e))
                        # Create a basic panel entry even if vision fails
                        all_panels.append({
                            "page_id": page.id,
                            "image_path": image_path,
                            "scene_type": "normal",
                            "speech_bubbles": [],
                        })
                else:
                    logger.warning("page_image_missing", page_id=page.id, path=image_path)

                pipeline_jobs[job_id].progress = 15.0 + (i / max(1, len(pages))) * 10.0

            # Step 3: OCR — extract text from vision results (local, no LLM)
            pipeline_jobs[job_id].current_step = "ocr"
            pipeline_jobs[job_id].progress = 30.0
            pipeline_jobs[job_id].message = "Extracting text..."

            ocr_text = ""
            for panel in all_panels:
                if panel.get("speech_bubbles"):
                    for bubble in panel["speech_bubbles"]:
                        ocr_text += bubble.get("text", "") + "\n"

            # Step 4: Story analysis — 1 consolidated LLM call
            pipeline_jobs[job_id].current_step = "story_analysis"
            pipeline_jobs[job_id].progress = 40.0
            pipeline_jobs[job_id].message = "Analyzing story (1 LLM call)..."

            from modules.story.consolidated import analyze_story_consolidated

            story_data = await analyze_story_consolidated(
                ocr_text=ocr_text,
                panels=all_panels,
                chapter_number=chapters[0].chapter_number if chapters else 1,
            )

            logger.info("story_analysis_result", type=type(story_data).__name__, has_scenes="scenes" in story_data if isinstance(story_data, dict) else False)

            # Step 5: Narration script — 1 consolidated LLM call
            pipeline_jobs[job_id].current_step = "narration"
            pipeline_jobs[job_id].progress = 55.0
            pipeline_jobs[job_id].message = "Generating narration (1 LLM call)..."

            from modules.story.consolidated import generate_narration_consolidated

            narration_result = await generate_narration_consolidated(
                story_analysis=story_data,
                style=style,
                max_duration_minutes=5,
            )

            logger.info("narration_result", type=type(narration_result).__name__, keys=list(narration_result.keys()) if isinstance(narration_result, dict) else "not_dict")

            # Extract script text from narration segments
            narration_segments = narration_result.get("segments", []) if narration_result else []
            logger.info("narration_segments_count", count=len(narration_segments))
            script_text = "\n\n".join([s.get("text", "") for s in narration_segments])

            # Step 6: Voice generation — Edge TTS (free, no API calls)
            pipeline_jobs[job_id].current_step = "voice_generation"
            pipeline_jobs[job_id].progress = 65.0
            pipeline_jobs[job_id].message = "Generating voice (Edge TTS, free)..."

            import edge_tts as _edge_tts

            audio_files = []
            audio_dir = Path(output_dir) / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            for i, segment in enumerate(narration_segments):
                text = segment.get("text", "")
                if not text:
                    continue

                try:
                    communicate = _edge_tts.Communicate(text, voice)
                    audio_data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data += chunk["data"]

                    if audio_data and len(audio_data) > 0:
                        audio_path = audio_dir / f"segment_{i:04d}.mp3"
                        audio_path.write_bytes(audio_data)
                        audio_files.append(str(audio_path))
                    else:
                        logger.warning("tts_empty_audio", segment=i)
                except Exception as e:
                    logger.warning("tts_segment_failed", segment=i, error=str(e), type=type(e).__name__)

                pipeline_jobs[job_id].progress = 65.0 + (i / max(1, len(narration_segments))) * 10.0

            logger.info("voice_generation_done", audio_count=len(audio_files))
            if not audio_files:
                logger.warning("no_audio_generated", segments=len(narration_segments))

            # Stitch audio with FFmpeg
            master_audio = audio_dir / "master_narration.mp3"
            if audio_files:
                # Ensure FFmpeg is findable
                ffmpeg_path = shutil.which("ffmpeg")
                if not ffmpeg_path:
                    # Try common Windows locations
                    for candidate in [
                        r"C:\ffmpeg\bin\ffmpeg.exe",
                        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                    ]:
                        if os.path.exists(candidate):
                            ffmpeg_path = candidate
                            break

                if ffmpeg_path and len(audio_files) == 1:
                    # Single file, just copy
                    shutil.copy2(audio_files[0], str(master_audio))
                elif ffmpeg_path and len(audio_files) > 1:
                    concat_file = audio_dir / "concat.txt"
                    with open(concat_file, "w") as f:
                        for af in audio_files:
                            f.write(f"file '{af}'\n")
                    try:
                        subprocess.run(
                            [ffmpeg_path, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(master_audio)],
                            capture_output=True, timeout=60,
                        )
                    except Exception as e:
                        logger.warning("ffmpeg_concat_failed", error=str(e))
                        # Fallback: just use first segment
                        shutil.copy2(audio_files[0], str(master_audio))
                    finally:
                        concat_file.unlink(missing_ok=True)
                elif audio_files:
                    # No FFmpeg, just use first segment
                    shutil.copy2(audio_files[0], str(master_audio))

            # Step 7-9: Timeline + Video — wrapped in try/except, audio always saved
            final_output = None
            try:
                # Step 7: Timeline composition
                pipeline_jobs[job_id].current_step = "timeline"
                pipeline_jobs[job_id].progress = 80.0
                pipeline_jobs[job_id].message = "Composing timeline..."

                from modules.timeline.agents.scene_composition import SceneCompositionAgent
                composition_agent = SceneCompositionAgent()

                scenes = []
                for panel in all_panels:
                    try:
                        scene_meta = composition_agent.analyze_scene(
                            {"emotion": "neutral", "scene_type": "normal"},
                            [{"panels": [panel]}],
                        )
                        duration = composition_agent.estimate_duration({"scene_type": "normal"}, "", 1)
                        cam_effect = "zoom_in"
                        if scene_meta and hasattr(scene_meta, "config") and scene_meta.config:
                            cam_effect = scene_meta.config.get("camera_effect", "zoom_in")
                        scenes.append({"panel": panel, "duration": duration, "camera_effect": cam_effect})
                    except Exception:
                        scenes.append({"panel": panel, "duration": 4.0, "camera_effect": "zoom_in"})

                logger.info("timeline_done", scene_count=len(scenes), panel_count=len(all_panels))

                # Step 8: Video rendering
                pipeline_jobs[job_id].current_step = "video_rendering"
                pipeline_jobs[job_id].progress = 85.0
                pipeline_jobs[job_id].message = f"Rendering {len(scenes)} scenes..."

                from modules.video.agents.scene_renderer import SceneRendererAgent, SceneRendererInput
                scene_renderer = SceneRendererAgent()
                width, height = resolution.split("x")
                scene_clips = []
                video_dir = Path(output_dir) / "scenes"
                video_dir.mkdir(parents=True, exist_ok=True)
                video_dir_abs = video_dir.resolve()

                for i, scene in enumerate(scenes):
                    panel = scene["panel"]
                    image_path = panel.get("image_path", "")
                    if image_path and os.path.exists(image_path):
                        clip_path = str(video_dir_abs / f"scene_{i:04d}.mp4")
                        renderer_input = SceneRendererInput(
                            image_path=image_path,
                            audio_path=str(master_audio) if i == 0 else None,
                            output_path=clip_path,
                            duration=scene["duration"],
                            width=int(width), height=int(height),
                            fps=fps, camera_effect=scene["camera_effect"],
                        )
                        try:
                            await scene_renderer.execute(renderer_input)
                            scene_clips.append(clip_path)
                        except Exception as e:
                            logger.warning("scene_render_failed", scene=i, error=str(e))
                    pipeline_jobs[job_id].progress = 85.0 + (i / max(1, len(scenes))) * 10.0

                # Step 9: Final encoding
                pipeline_jobs[job_id].current_step = "final_encoding"
                pipeline_jobs[job_id].progress = 95.0
                final_output = Path(output_dir) / f"manga_{manga_id}_final.mp4"
                final_output_abs = final_output.resolve()

                if scene_clips:
                    concat_file = video_dir_abs / "concat.txt"
                    with open(concat_file, "w") as f:
                        for clip in scene_clips:
                            f.write(f"file '{clip}'\n")
                    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
                    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", str(final_output_abs)], capture_output=True, timeout=300)
                    concat_file.unlink(missing_ok=True)

            except Exception as e:
                logger.warning("video_pipeline_error", error=str(e))

            # Complete — audio is always saved regardless of video success
            pipeline_jobs[job_id].status = "completed"
            pipeline_jobs[job_id].progress = 100.0
            pipeline_jobs[job_id].current_step = "completed"
            pipeline_jobs[job_id].message = "Pipeline completed!"
            pipeline_jobs[job_id].output_path = str(final_output_abs) if final_output and final_output_abs.exists() else str(master_audio)

            logger.info(
                "pipeline_completed",
                job_id=job_id,
                manga_id=manga_id,
                output=str(final_output),
            )

    except Exception as e:
        pipeline_jobs[job_id].status = "failed"
        pipeline_jobs[job_id].error = str(e)
        pipeline_jobs[job_id].message = f"Pipeline failed: {str(e)}"
        logger.error("pipeline_failed", job_id=job_id, error=str(e))


@router.post(
    "/run",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run full manga-to-video pipeline",
    description="Executes the complete pipeline from manga to final video.",
)
async def run_pipeline(
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Start the full manga-to-video pipeline."""
    job_id = int(datetime.utcnow().timestamp() * 1000) % 100000

    # Validate manga exists
    stmt = select(Manga).where(Manga.id == request.manga_id)
    result = await db.execute(stmt)
    manga = result.scalar_one_or_none()

    if not manga:
        raise HTTPException(status_code=404, detail=f"Manga {request.manga_id} not found")

    # Create output directory
    output_dir = Path(request.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Start pipeline in background
    background_tasks.add_task(
        _run_full_pipeline,
        job_id=job_id,
        manga_id=request.manga_id,
        chapter_id=request.chapter_id,
        output_dir=str(output_dir),
        voice=request.voice,
        style=request.style,
        resolution=request.resolution,
        fps=request.fps,
        max_pages=request.max_pages,
    )

    pipeline_jobs[job_id] = PipelineStatus(
        job_id=job_id,
        status="queued",
        current_step="queued",
        progress=0.0,
        message="Pipeline queued...",
    )

    logger.info(
        "pipeline_queued",
        job_id=job_id,
        manga_id=request.manga_id,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Pipeline started for manga '{manga.title}'",
        "manga_id": request.manga_id,
    }


@router.get(
    "/status/{job_id}",
    summary="Get pipeline status",
    description="Retrieves the current status of a running pipeline.",
)
async def get_pipeline_status(job_id: int) -> Dict[str, Any]:
    """Get pipeline execution status."""
    if job_id not in pipeline_jobs:
        raise HTTPException(status_code=404, detail=f"Pipeline job {job_id} not found")

    status_info = pipeline_jobs[job_id]

    return {
        "job_id": status_info.job_id,
        "status": status_info.status,
        "current_step": status_info.current_step,
        "progress": status_info.progress,
        "message": status_info.message,
        "output_path": status_info.output_path,
        "error": status_info.error,
    }


@router.get(
    "/jobs",
    summary="List all pipeline jobs",
    description="Lists all pipeline jobs and their status.",
)
async def list_pipeline_jobs() -> List[Dict[str, Any]]:
    """List all pipeline jobs."""
    return [
        {
            "job_id": s.job_id,
            "status": s.status,
            "current_step": s.current_step,
            "progress": s.progress,
            "message": s.message,
        }
        for s in pipeline_jobs.values()
    ]
