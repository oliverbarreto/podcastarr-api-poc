from typing import Dict, Optional, Tuple
from datetime import datetime
from ..lib.ytdlp.youtube_downloader_ytdlp import YouTubeDownloaderYTDLP
from ..core.logger import get_logger

logger = get_logger("services.youtube_download")


class YouTubeDownloadService:
    def __init__(self):
        self.downloader = YouTubeDownloaderYTDLP()

    def _parse_youtube_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Convert YouTube date format (YYYYMMDD) to datetime"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            return None

    async def extract_video_info(self, url: str) -> Optional[Dict]:
        """
        Extract and format video information for database storage

        Args:
            url: YouTube URL

        Returns:
            Dict with formatted video information or None if extraction fails
        """
        try:
            info = await self.downloader.extract_video_info(url)
            if not info:
                return None

            # Convert YouTube date format to datetime
            published_at = self._parse_youtube_date(info.get("published_at"))

            return {
                "video_id": info["video_id"],
                "title": info["title"],
                "subtitle": info.get("subtitle"),
                "summary": info.get("summary"),
                "author": info.get("author"),
                "channel": info["channel"],
                "keywords": info.get("keywords"),
                "image_url": info.get("image_url"),
                "published_at": published_at,
                "duration": info["duration"],
                "explicit": info.get("explicit", False),
                "position": info.get("position", 0),
                "status": "pending",  # Initial status
            }

        except Exception as e:
            logger.error(f"Error extracting video info: {str(e)}")
            return None

    async def download_audio(self, url: str, video_id: str) -> Tuple[bool, Dict]:
        """
        Download audio from a YouTube URL

        Args:
            url: YouTube URL
            video_id: Video ID for file naming

        Returns:
            Tuple[bool, Dict]: (success, result_data)
                success: Whether the operation was successful
                result_data: Dict containing download results or error information
        """
        try:
            result = await self.downloader.download_audio(url, video_id)

            if result["success"]:
                return True, {
                    "media_url": result["media_url"],
                    "media_size": result["media_size"],
                    "media_length": result["media_size"],  # For compatibility
                }

            return False, {"error": result.get("error", "Unknown error")}

        except Exception as e:
            logger.error(f"Error in download service: {str(e)}")
            return False, {"error": str(e)}
