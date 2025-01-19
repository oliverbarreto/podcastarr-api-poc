from typing import Optional, Dict, Any

import pytubefix

from ..utils import extract_video_id
from ...core.logger import get_logger

logger = get_logger("lib.pytubefix.youtube_service")


class YouTubeService:
    """Service for interacting with YouTube and extracting metadata"""

    @staticmethod
    def get_video_metadata(url: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a YouTube video URL

        Args:
            url (str): The YouTube URL

        Returns:
            Optional[Dict[str, Any]]: Video metadata or None if extraction fails
        """
        try:
            # Extract video ID
            video_id = extract_video_id(url)
            if not video_id:
                logger.error(f"Could not extract video ID from URL: {url}")
                return None

            # Get video metadata
            # yt = pytubefix.YouTube(url)

            proxies = {
                "http": "HTTP://130.162.180.254:8888",
            }
            yt = pytubefix.YouTube(url, proxies=proxies)

            return {
                "video_id": video_id,
                "title": yt.title,
                "author": yt.author,
                "description": yt.description,
                "thumbnail_url": yt.thumbnail_url,
                "keywords": (
                    ",".join(yt.keywords)
                    if hasattr(yt, "keywords") and yt.keywords
                    else None
                ),
                "length": yt.length,
            }
        except Exception as e:
            logger.error(f"Error extracting metadata from YouTube: {str(e)}")
            return None

    @staticmethod
    def get_audio_stream(url: str) -> Optional[pytubefix.Stream]:
        """Get the best audio stream for a YouTube video"""
        try:
            yt = pytubefix.YouTube(url)
            return yt.streams.get_audio_only()
        except Exception as e:
            logger.error(f"Error getting audio stream: {str(e)}")
            return None
