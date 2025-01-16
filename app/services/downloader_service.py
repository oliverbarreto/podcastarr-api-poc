import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any

from ..core.logger import get_logger

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")

logger = get_logger("services.download_service")


class DownloadService:
    @staticmethod
    def create_download(
        download_id: str, url: str, video_id: str, video_name: str, filename: str
    ) -> Dict[str, Any]:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO downloads (id, url, video_id, videoname, filename, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    download_id,
                    str(url),
                    video_id,
                    video_name,
                    filename,
                    "pending",
                    datetime.utcnow(),
                ),
            )
            conn.commit()
            return {
                "id": download_id,
                "url": url,
                "video_id": video_id,
                "status": "pending",
            }
        finally:
            conn.close()

    @staticmethod
    def get_download_status(download_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        try:
            c.execute(
                """
                SELECT id, url, video_id, videoname, status, filename, 
                       created_at, completed_at 
                FROM downloads 
                WHERE id = ?
                """,
                (download_id,),
            )
            result = c.fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "url": result[1],
                "video_id": result[2],
                "videoname": result[3],
                "status": result[4],
                "filename": result[5],
                "created_at": datetime.fromisoformat(result[6]) if result[6] else None,
                "completed_at": (
                    datetime.fromisoformat(result[7]) if result[7] else None
                ),
            }
        finally:
            conn.close()

    @staticmethod
    def get_completed_downloads() -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        try:
            c.execute(
                """
                SELECT id, url, video_id, videoname, status, filename, created_at, completed_at 
                FROM downloads 
                WHERE status = 'completed' 
                AND filename IS NOT NULL
                """
            )
            db_files = c.fetchall()

            files = []
            for db_file in db_files:
                (
                    download_id,
                    url,
                    video_id,
                    videoname,
                    status,
                    filename,
                    created_at,
                    completed_at,
                ) = db_file

                file_path = os.path.join(DOWNLOADS_PATH, filename)
                if os.path.exists(file_path):
                    file_stats = os.stat(file_path)
                    files.append(
                        {
                            "id": download_id,
                            "url": url,
                            "filename": filename,
                            "filepath": file_path,
                            "size": file_stats.st_size,
                            "created_at": (
                                datetime.fromisoformat(created_at)
                                if created_at
                                else None
                            ),
                            "completed_at": (
                                datetime.fromisoformat(completed_at)
                                if completed_at
                                else None
                            ),
                            "video_id": video_id,
                            "videoname": videoname,
                            "status": status,
                        }
                    )
            return files
        finally:
            conn.close()
