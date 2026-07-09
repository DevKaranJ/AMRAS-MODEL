import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.youtube import Playlist

logger = logging.getLogger(__name__)


class PlaylistAgent:
    """
    Automatically manages Series, Parts, Playlists, and Ordering.
    """

    def __init__(self, youtube_client: Any = None) -> None:
        self.youtube = youtube_client  # Placeholder for actual API client

    async def get_or_create_playlist(
        self, db: AsyncSession, manga_id: int, series_title: str
    ) -> Playlist:
        """Find an existing playlist for a manga or create a new one, persisting to DB."""
        logger.info(f"Looking up or creating playlist for manga {manga_id}: {series_title}")

        result = await db.execute(select(Playlist).where(Playlist.manga_id == manga_id))
        playlist = result.scalars().first()

        if playlist:
            logger.info(f"Found existing playlist: {playlist.youtube_playlist_id}")
            return playlist

        # Assume we made a YT API request here
        yt_playlist_id = f"PL_mock_{manga_id}"

        playlist = Playlist(
            manga_id=manga_id,
            youtube_playlist_id=yt_playlist_id,
            title=f"{series_title} - Full Series Recap",
            description=f"All parts of the {series_title} manga recap.",
            visibility="public",
        )
        db.add(playlist)
        await db.flush()

        logger.info(f"Created new playlist: {yt_playlist_id}")
        return playlist

    async def add_video_to_playlist(
        self, playlist_id: str, video_id: str, position: Optional[int] = None
    ) -> bool:
        """Add a video to a specific playlist and maintain order."""
        logger.info(f"Adding video {video_id} to playlist {playlist_id} at position {position}")
        # External API mock call
        return True
