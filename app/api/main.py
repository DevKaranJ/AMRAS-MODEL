from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.endpoints.ingestion import router as ingestion_router
from app.api.endpoints.memory import router as memory_router
from app.api.endpoints.ocr import router as ocr_router
from app.api.endpoints.story import router as story_router
from app.api.endpoints.subtitles import router as subtitles_router
from app.api.endpoints.thumbnails import router as thumbnails_router
from app.api.endpoints.timeline import router as timeline_router
from app.api.endpoints.video import router as video_router
from app.api.endpoints.vision import router as vision_router
from app.api.endpoints.voice import router as voice_router
from app.api.endpoints.youtube import router as youtube_router
from app.config.settings import settings
from app.core.exceptions import AmrasException
from app.core.logger import get_logger, setup_logging

setup_logging()
logger = get_logger("amras.api")

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="API for AI Manga Recap Automation System",
)

app.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
app.include_router(vision_router, prefix="/vision", tags=["vision"])
app.include_router(memory_router, prefix="/memory", tags=["memory"])

app.include_router(ocr_router, prefix="/ocr", tags=["ocr"])
app.include_router(story_router, prefix="/story", tags=["story"])
app.include_router(voice_router, prefix="/audio", tags=["voice"])
app.include_router(timeline_router, prefix="/timeline", tags=["timeline"])
app.include_router(video_router, prefix="/render", tags=["video"])
app.include_router(subtitles_router, prefix="/subtitles", tags=["subtitles"])
app.include_router(youtube_router, tags=["youtube", "publishing"])
app.include_router(thumbnails_router, prefix="/thumbnail", tags=["thumbnails"])


@app.exception_handler(AmrasException)
async def amras_exception_handler(request: Request, exc: AmrasException) -> JSONResponse:
    path = str(request.url.path).encode("unicode_escape").decode("utf-8")
    logger.error("amras_exception", error=exc.to_dict(), path=path)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.to_dict()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    path = str(request.url.path).encode("unicode_escape").decode("utf-8")
    msg = str(exc).encode("unicode_escape").decode("utf-8")
    logger.exception("unhandled_exception", error=msg, path=path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
    )


@app.get("/health", tags=["system"])
async def health_check() -> Dict[str, Any]:
    return {"status": "ok"}


@app.get("/version", tags=["system"])
async def version() -> Dict[str, Any]:
    return {"version": settings.version}


@app.get("/settings", tags=["system"])
async def get_app_settings() -> Dict[str, Any]:
    data = settings.model_dump()
    # Redact sensitive values
    if "ai" in data and "api_key" in data["ai"]:
        data["ai"]["api_key"] = "***"
    if "db" in data and "url" in data["db"]:
        data["db"]["url"] = "***"
    return data


# Skeleton jobs endpoints
@app.post("/jobs", tags=["jobs"])
async def create_job() -> Dict[str, Any]:
    return {"status": "queued", "job_id": "123"}


@app.get("/jobs/{job_id}", tags=["jobs"])
async def get_job(job_id: str) -> Dict[str, Any]:
    return {"job_id": job_id, "status": "running"}
