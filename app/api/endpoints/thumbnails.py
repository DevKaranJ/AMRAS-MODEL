from datetime import datetime, timezone
from typing import Any, List

from fastapi import APIRouter, status

from app.schemas.youtube import GenerateThumbnailRequest, ThumbnailResponse

router = APIRouter()


@router.post("/generate", response_model=List[ThumbnailResponse], status_code=status.HTTP_202_ACCEPTED)
async def generate_thumbnails(request: GenerateThumbnailRequest) -> Any:
    """
    Trigger the thumbnail generation pipeline (Planning and Composition).
    Returns a list of potential thumbnail base structures (mocked async response).
    """
    # Mocking behavior
    return [
        ThumbnailResponse(
            id=1,
            job_id=request.project_id,
            scene_id=10,
            base_image_path="storage/thumbnail/10.png",
            score=95.0,
            variants=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]


@router.get("", response_model=List[ThumbnailResponse])
async def list_thumbnails(project_id: int) -> Any:
    """
    Retrieve generated thumbnails for a specific project.
    """
    return []
