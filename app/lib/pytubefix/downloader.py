import os
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from ...core.logger import get_logger
from .youtube_service import YouTubeService

# Load environment variables
load_dotenv()
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")

logger = get_logger("lib.pytubefix.downloader")


class YouTubeDownloader:
    """Handles YouTube video downloads using PyTubeFix"""

    def __init__(self):
        self.youtube_service = YouTubeService()

    async def download_audio(self, url: str, video_id: str) -> Dict[str, Any]:
        """
        Downloads audio for a given YouTube URL

        Args:
            url (str): YouTube URL
            video_id (str): Video ID to use for the filename

        Returns:
            Dict with download results containing:
            - success (bool): Whether download was successful
            - media_url (str): Local path to the downloaded file
            - media_size (int): Size of the downloaded file
            - media_duration (int): Duration of the audio
            - media_length (int): Size of the audio stream
            - error (str): Error message if download failed
        """
        try:
            # Get audio stream
            audio_stream = self.youtube_service.get_audio_stream(url)
            if not audio_stream:
                return {"success": False, "error": f"No audio stream found for {url}"}

            # Generate filename and path
            filename = f"{video_id}.mp3"
            file_path = os.path.join(DOWNLOADS_PATH, filename)

            # Download audio
            logger.info(f"Downloading audio for video {video_id}")
            audio_stream.download(output_path=DOWNLOADS_PATH, filename=filename)

            # Get metadata
            metadata = self.youtube_service.get_video_metadata(url)

            return {
                "success": True,
                "media_url": f"/audio/{filename}",
                "media_size": os.path.getsize(file_path),
                "media_duration": metadata.get("length") if metadata else None,
                "media_length": audio_stream.filesize,
            }

        except Exception as e:
            error_msg = f"Error downloading audio: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
