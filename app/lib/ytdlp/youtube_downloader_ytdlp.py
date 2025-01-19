import os
from typing import Dict, Optional
from pathlib import Path

import yt_dlp

from ...core.logger import get_logger

logger = get_logger("lib.ytdlp.downloader")


class YouTubeDownloaderYTDLP:
    """
    YouTube Downloader using yt-dlp
    """

    def __init__(self):
        self.download_path = os.getenv("DOWNLOAD_PATH", "./downloads")
        self.audio_format = os.getenv("AUDIO_FORMAT", "m4a")

        Path(self.download_path).mkdir(parents=True, exist_ok=True)

    def _get_download_opts(self, video_id: str) -> Dict:
        """Configure yt-dlp options for audio download"""
        return {
            "format": f"{self.audio_format}/bestaudio/best",
            "paths": {"home": self.download_path},
            "logger": logger,
            "progress_hooks": [self._progress_hook],
            "outtmpl": {"default": f"{video_id}.%(ext)s"},
        }

    # def _get_ydl_opts(self, video_id: str) -> Dict:
    #     return {
    #         "format": f"{self.audio_format}/bestaudio/best",
    #         "paths": {"home": self.download_path},
    #         "outtmpl": {"default": f"{video_id}.%(ext)s"},
    #         "logger": logger,
    #         "progress_hooks": [self._progress_hook],
    #         "postprocessors": [
    #             {
    #                 "key": "FFmpegExtractAudio",
    #                 "preferredcodec": self.audio_format,
    #             }
    #         ],
    #     }

    def _progress_hook(self, d: dict):
        """Handle download progress updates"""

        video_id = d.get("info_dict", {}).get("id", "N/A")
        title = d.get("info_dict", {}).get("title", "N/A")

        if d["status"] == "downloading":
            try:
                progress = float(d["_percent_str"].replace("%", ""))
                logger.info(f"[{video_id}] Downloading '{title}': {progress:.1f}%")

            except:
                pass

        elif d["status"] == "finished":
            logger.info(f"[{video_id}] Download completed for '{title}'")

        elif d["status"] == "error":
            logger.error(f"[{video_id}] Error downloading '{title}': {d.get('error')}")

    async def extract_video_info(self, url: str) -> Optional[Dict]:
        """
        Extract video information without downloading

        Returns a dictionary with all necessary fields for Episode model:
        - video_id: YouTube video ID
        - title: Video title
        - subtitle: Video subtitle/short description
        - summary: Full video description
        - author: Channel name
        - channel: Channel name (for compatibility)
        - keywords: Video tags joined by comma
        - image_url: Thumbnail URL (highest quality)
        - published_at: Video publish date
        - duration: Video duration in seconds
        - explicit: Always False for YouTube
        """
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)

                # Get best thumbnail
                thumbnails = info.get("thumbnails", [])
                best_thumbnail = (
                    max(thumbnails, key=lambda x: x.get("height", 0))
                    if thumbnails
                    else {}
                )

                # Get all tags/keywords
                keywords = ", ".join(info.get("tags", [])) if info.get("tags") else None

                return {
                    "video_id": info.get("id"),
                    "title": info.get("title"),
                    "subtitle": (
                        info.get("description", "")[:100] + "..."
                        if info.get("description")
                        else None
                    ),  # First 100 chars
                    "summary": info.get("description"),
                    "author": info.get("channel"),
                    "channel": info.get("channel"),  # For compatibility
                    "keywords": keywords,
                    "image_url": best_thumbnail.get("url") or info.get("thumbnail"),
                    "published_at": info.get("upload_date"),  # YYYYMMDD format
                    "duration": info.get("duration", 0),
                    "explicit": False,  # YouTube videos are not marked explicit
                    "position": 0,  # Default position
                }
        except Exception as e:
            logger.error(f"Error extracting video info: {str(e)}")
            return None

    async def download_audio(self, url: str, video_id: str) -> Dict:
        """Download audio from a YouTube URL"""
        try:
            ydl_opts = self._get_download_opts(video_id)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Get the downloaded file info using the actual download path
            file_path = os.path.join(
                self.download_path, f"{video_id}.{self.audio_format}"
            )
            file_size = os.path.getsize(file_path)

            return {
                "success": True,
                "file_path": file_path,
                "media_url": file_path,  # Use the actual file path
                "media_size": file_size,
            }
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return {"success": False, "error": str(e)}
