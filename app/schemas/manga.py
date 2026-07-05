from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MangaMetadata(BaseModel):
    title: str
    slug: str
    language: Optional[str] = None
    author: Optional[str] = None
    artist: Optional[str] = None
    status: str = "ongoing"
    hash: Optional[str] = None


class MangaCreate(MangaMetadata):
    pass


class MangaRead(MangaMetadata):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    chapters: List["ChapterRead"] = []


class ChapterCreate(BaseModel):
    manga_id: int
    chapter_number: float
    volume: Optional[int] = None
    title: Optional[str] = None
    page_count: int = 0
    imported: bool = False


class ChapterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manga_id: int
    chapter_number: float
    volume: Optional[int] = None
    title: Optional[str] = None
    page_count: int
    imported: bool
    created_at: datetime
    updated_at: datetime


class PageCreate(BaseModel):
    chapter_id: int
    page_number: int
    image_path: str
    width: Optional[int] = None
    height: Optional[int] = None
    image_hash: Optional[str] = None


class PageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: int
    page_number: int
    image_path: str
    width: Optional[int]
    height: Optional[int]
    image_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

MangaRead.model_rebuild()
