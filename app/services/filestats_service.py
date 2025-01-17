from datetime import datetime
import sqlite3
from typing import List, Optional
from ..core.logger import get_logger
from dotenv import load_dotenv
import os

logger = get_logger("services.filestats_service")

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


class FileStats:
    def __init__(self):
        self.db_path = DATABASE_PATH

    async def record_access(self, filename: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO file_access (filename, last_accessed)
                    VALUES (?, CURRENT_TIMESTAMP)
                    ON CONFLICT(filename) DO UPDATE SET
                        access_count = access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP
                """,
                    (filename,),
                )

        except Exception as e:
            logger.error(f"Error recording file access: {e}")
            raise

    async def get_stats(self, skip: int = 0, limit: int = 10) -> List[dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT filename, access_count, last_accessed
                    FROM file_access
                    ORDER BY access_count DESC
                    LIMIT ? OFFSET ?
                """,
                    (limit, skip),
                )
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
            raise

    async def get_total_count(self) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM file_access")
                return cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Error getting total count: {e}")
            raise

    async def get_file_stats(self, filename: str) -> Optional[dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT filename, access_count, last_accessed
                    FROM file_access
                    WHERE filename = ?
                """,
                    (filename,),
                )
                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
            raise
