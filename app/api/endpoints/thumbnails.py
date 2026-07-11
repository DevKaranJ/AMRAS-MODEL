from typing import Any, List

from fastapi import APIRouter, HTTPException, status

from app.schemas.youtube import GenerateThumbnailRequest, ThumbnailResponse

router = APIRouter()


@router.post("/generate", response_model=List[ThumbnailResponse], status_code=status.HTTP_202_ACCEPTED)
async def generate_thumbnails(request: GenerateThumbnailRequest) -> Any:
    """
    Trigger the thumbnail generation pipeline (Planning and Composition).
    Returns a list of potential thumbnail base structures (mocked async response).
    """
    # TODO: Implement real thumbnail generation pipeline
    # Should use request.number_of_variants, request.style, etc.
    # to delegate to thumbnail agents (PlanningAgent, CompositionAgent)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Thumbnail generation pipeline not yet implemented"
    )


@router.get("", response_model=List[ThumbnailResponse])
async def list_thumbnails(project_id: int) -> Any:
    """
    Retrieve generated thumbnails for a specific project.
    """
    # TODO: Query database for thumbnails by project_id
    # Should query Thumbnail model and related variants from persistence layer
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Thumbnail listing not yet implemented")
