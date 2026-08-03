from typing import Any

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints.ingestion import router as ingestion_router
from app.api.endpoints.memory import router as memory_router
from app.api.endpoints.ocr import router as ocr_router
from app.api.endpoints.pipeline import router as pipeline_router
from app.api.endpoints.production import router as production_router
from app.api.endpoints.qa import router as qa_router
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
from app.core.security import require_api_key

setup_logging()
logger = get_logger("amras.api")

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="API for AI Manga Recap Automation System",
)


@app.on_event("startup")
async def startup_register_providers() -> None:
    from app.shared.providers.base import ensure_providers_registered
    ensure_providers_registered()

# ---------------------------------------------------------------------- #
# CORS middleware                                                          #
# ---------------------------------------------------------------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# ---------------------------------------------------------------------- #
# Authenticated routers — every domain router requires a valid API key    #
# ---------------------------------------------------------------------- #
_auth = [Depends(require_api_key)]

app.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"], dependencies=_auth)
app.include_router(vision_router, prefix="/vision", tags=["vision"], dependencies=_auth)
app.include_router(memory_router, prefix="/memory", tags=["memory"], dependencies=_auth)
app.include_router(ocr_router, prefix="/ocr", tags=["ocr"], dependencies=_auth)
app.include_router(story_router, prefix="/story", tags=["story"], dependencies=_auth)
app.include_router(voice_router, prefix="/audio", tags=["voice"], dependencies=_auth)
app.include_router(timeline_router, prefix="/timeline", tags=["timeline"], dependencies=_auth)
app.include_router(video_router, prefix="/render", tags=["video"], dependencies=_auth)
app.include_router(subtitles_router, prefix="/subtitles", tags=["subtitles"], dependencies=_auth)
app.include_router(youtube_router, tags=["youtube", "publishing"], dependencies=_auth)
app.include_router(thumbnails_router, prefix="/thumbnail", tags=["thumbnails"], dependencies=_auth)
app.include_router(qa_router, prefix="/qa", tags=["qa"], dependencies=_auth)
app.include_router(production_router, prefix="/production", tags=["production"], dependencies=_auth)
app.include_router(pipeline_router, prefix="/pipeline", tags=["pipeline"], dependencies=_auth)


# ---------------------------------------------------------------------- #
# Exception handlers                                                      #
# ---------------------------------------------------------------------- #
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


# ---------------------------------------------------------------------- #
# Public (unauthenticated) system endpoints                               #
# ---------------------------------------------------------------------- #
@app.get("/health", tags=["system"])
async def health_check() -> Any:
    """Liveness probe — returns 200 when the server is running."""
    return {"status": "ok"}


@app.get("/version", tags=["system"])
async def version() -> Any:
    return {"version": settings.version}


@app.get("/settings", tags=["system"])
async def get_app_settings() -> Any:
    data = settings.model_dump()
    # Redact all sensitive values before returning
    if "ai" in data and "api_key" in data["ai"]:
        data["ai"]["api_key"] = "***"
    if "db" in data and "url" in data["db"]:
        data["db"]["url"] = "***"
    if "api_key" in data:
        data["api_key"] = "***"
    return data


# ---------------------------------------------------------------------- #
# Skeleton jobs endpoints (authenticated)                                 #
# ---------------------------------------------------------------------- #
@app.post("/jobs", tags=["jobs"], dependencies=_auth)
async def create_job() -> Any:
    return {"status": "queued", "job_id": "123"}


@app.get("/jobs/{job_id}", tags=["jobs"], dependencies=_auth)
async def get_job(job_id: str) -> Any:
    return {"job_id": job_id, "status": "running"}
