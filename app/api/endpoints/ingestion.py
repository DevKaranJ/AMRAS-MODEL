from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ImportRequest(BaseModel):
    source_path: str

class DownloadRequest(BaseModel):
    manga_id: str
    chapter_id: str
    dest_dir: str

@router.post("/import", status_code=202)
async def import_manga(req: ImportRequest) -> Dict[str, Any]:
    """Starts an import job from a local source path."""
    # This would enqueue the job in a real implementation
    return {"message": "Import job queued", "source_path": req.source_path, "job_id": 1}

@router.post("/download", status_code=202)
async def download_manga(req: DownloadRequest) -> Dict[str, Any]:
    """Starts a download job for a specific chapter."""
    # This would enqueue the job in a real implementation
    return {"message": "Download job queued", "manga_id": req.manga_id, "chapter_id": req.chapter_id, "job_id": 2}

@router.get("/manga")
async def list_manga() -> List[Dict[str, Any]]:
    """Lists imported manga."""
    # Retrieve from DB in real implementation
    return [{"id": 1, "title": "Sample Manga"}]
