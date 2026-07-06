from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Manga(Base, TimestampMixin):
    __tablename__ = "mangas"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    language: Mapped[Optional[str]] = mapped_column(String(50))
    author: Mapped[Optional[str]] = mapped_column(String(255))
    artist: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="ongoing")
    hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    chapters: Mapped[list["Chapter"]] = relationship("Chapter", back_populates="manga", cascade="all, delete-orphan")


class Chapter(Base, TimestampMixin):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True)
    manga_id: Mapped[int] = mapped_column(ForeignKey("mangas.id", ondelete="CASCADE"), index=True)
    chapter_number: Mapped[float] = mapped_column(Float, index=True)
    volume: Mapped[Optional[int]] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    imported: Mapped[bool] = mapped_column(Boolean, default=False)

    manga: Mapped["Manga"] = relationship("Manga", back_populates="chapters")
    pages: Mapped[list["Page"]] = relationship("Page", back_populates="chapter", cascade="all, delete-orphan")


class Page(Base, TimestampMixin):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"), index=True)
    page_number: Mapped[int] = mapped_column(Integer, index=True)
    image_path: Mapped[str] = mapped_column(String(1024))
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    image_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="pages")


class ImportJob(Base, TimestampMixin):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(50), index=True, default="queued")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_file: Mapped[Optional[str]] = mapped_column(String(1024))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error: Mapped[Optional[str]] = mapped_column(Text)


class DownloadJob(Base, TimestampMixin):
    __tablename__ = "download_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True, default="queued")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    retries: Mapped[int] = mapped_column(Integer, default=0)
    bandwidth: Mapped[Optional[float]] = mapped_column(Float)  # kbps or bytes/s
    error: Mapped[Optional[str]] = mapped_column(Text)
