import sqlite3
from datetime import datetime
import uuid
from typing import List, Optional
import os
from dotenv import load_dotenv

from ..models.episode import Episode, EpisodeCreate
from ..core.logger import get_logger
from ..lib.pytubefix.youtube_service import YouTubeService

from ..lib.utils import extract_video_id

logger = get_logger("services.episode")

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/downloads.db")


class EpisodeService:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.youtube_service = YouTubeService()

    def create_episode(self, episode_data: EpisodeCreate) -> Episode:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if episode already exists
            cursor.execute(
                "SELECT id FROM episodes WHERE video_id = ?", (episode_data.video_id,)
            )
            existing = cursor.fetchone()
            if existing:
                return self.get_episode_by_id(existing[0])

            episode_id = str(uuid.uuid4())
            now = datetime.utcnow()

            cursor.execute(
                """
                INSERT INTO episodes (
                    id, url, created_at, updated_at, status, 
                    video_id, title, subtitle, summary,
                    position, image_url, published_at, explicit,
                    author, keywords, media_duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    episode_id,
                    str(episode_data.url),
                    now,
                    now,
                    episode_data.status,
                    episode_data.video_id,
                    episode_data.title,
                    episode_data.subtitle,
                    episode_data.summary,
                    episode_data.position,
                    episode_data.image_url,
                    episode_data.published_at or now,
                    episode_data.explicit,
                    episode_data.author,
                    episode_data.keywords,
                    episode_data.duration,
                ),
            )

            conn.commit()
            return self.get_episode_by_id(episode_id)

        except Exception as e:
            logger.error(f"Error creating episode: {str(e)}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def get_episode_by_id(self, episode_id: str) -> Optional[Episode]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_episode(row)
        finally:
            conn.close()

    def get_episode_by_video_id(self, video_id: str) -> Optional[Episode]:
        """Get episode by video ID with all fields"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM episodes 
                WHERE video_id = ?
                """,
                (video_id,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_episode(row)

        except Exception as e:
            logger.error(f"Error getting episode by video ID: {str(e)}")
            return None

        finally:
            conn.close()

    def get_episodes(self, limit: int = 100, offset: int = 0) -> List[Episode]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM episodes ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            return [self._row_to_episode(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def get_episodes_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> List[Episode]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM episodes WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (status, limit, offset),
            )
            return [self._row_to_episode(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_episode_status(
        self,
        episode_id: str,
        status: str,
        media_url: Optional[str] = None,
        media_size: Optional[int] = None,
        media_duration: Optional[int] = None,
        media_length: Optional[int] = None,
    ) -> Optional[Episode]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            update_fields = ["status = ?", "updated_at = ?"]
            params = [status, datetime.utcnow()]

            if media_url is not None:
                update_fields.append("media_url = ?")
                params.append(media_url)

            if media_size is not None:
                update_fields.append("media_size = ?")
                params.append(media_size)

            if media_duration is not None:
                update_fields.append("media_duration = ?")
                params.append(media_duration)

            if media_length is not None:
                update_fields.append("media_length = ?")
                params.append(media_length)

            params.append(episode_id)

            cursor.execute(
                f"""
                UPDATE episodes 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """,
                params,
            )

            conn.commit()
            return self.get_episode_by_id(episode_id)

        finally:
            conn.close()

    def increment_access_count(self, episode_id: str) -> Optional[Episode]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE episodes 
                SET count = count + 1,
                    last_accessed_at = ?,
                    updated_at = ?
                WHERE id = ?
            """,
                (datetime.utcnow(), datetime.utcnow(), episode_id),
            )

            conn.commit()
            return self.get_episode_by_id(episode_id)

        finally:
            conn.close()

    def get_episodes_by_access(self, limit: int = 10, offset: int = 0) -> List[Episode]:
        """Get all episodes ordered by access count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM episodes 
                ORDER BY count DESC, last_accessed_at DESC NULLS LAST, created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            return [self._row_to_episode(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_total_episodes(self) -> int:
        """Get total number of episodes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM episodes")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def _row_to_episode(self, row) -> Episode:
        # Get column names from cursor description
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM episodes WHERE 1=0")
        columns = [description[0] for description in cursor.description]
        conn.close()

        # Create a dictionary mapping column names to values
        episode_dict = dict(zip(columns, row))

        # Convert to Episode model
        return Episode(
            id=uuid.UUID(episode_dict["id"]),
            url=episode_dict["url"],
            created_at=datetime.fromisoformat(episode_dict["created_at"]),
            updated_at=datetime.fromisoformat(episode_dict["updated_at"]),
            status=episode_dict["status"],
            tags=episode_dict["tags"],
            count=episode_dict["count"],
            last_accessed_at=(
                datetime.fromisoformat(episode_dict["last_accessed_at"])
                if episode_dict["last_accessed_at"]
                else None
            ),
            video_id=episode_dict["video_id"],
            title=episode_dict["title"],
            subtitle=episode_dict["subtitle"],
            summary=episode_dict["summary"],
            position=episode_dict["position"],
            image_url=episode_dict["image_url"],
            published_at=datetime.fromisoformat(episode_dict["published_at"]),
            explicit=bool(episode_dict["explicit"]),
            media_url=episode_dict["media_url"],
            media_size=episode_dict["media_size"],
            author=episode_dict["author"],
            keywords=episode_dict["keywords"],
            media_duration=episode_dict["media_duration"],
            media_length=episode_dict["media_length"],
        )

    def _extract_video_id(self, url: str) -> str:
        # Use the utility function
        video_id = extract_video_id(url)

        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")

        return video_id
