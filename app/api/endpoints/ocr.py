from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session

router = APIRouter()


class OCRProcessRequest(BaseModel):
    page_id: int


@router.post("/process", status_code=202)
async def process_ocr(req: OCRProcessRequest, session: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Starts an OCR job for a specific page."""
    # Similar to vision, queue job
    return {"message": "OCR job queued", "page_id": req.page_id}
