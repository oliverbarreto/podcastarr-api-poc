import os
from typing import Optional
from datetime import datetime
import pytubefix
from dotenv import load_dotenv

from ..core.logger import get_logger
from ..services.episode_service import EpisodeService

# Load environment variables
load_dotenv()
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")

logger = get_logger("services.downloader")


class Downloader:
    def __init__(self):
        self.episode_service = EpisodeService()

    async def download_audio(self, episode_id: str) -> bool:
        """Downloads audio for a given episode"""
        try:
            # Get episode
            episode = self.episode_service.get_episode_by_id(episode_id)
            if not episode:
                logger.error(f"Episode not found: {episode_id}")
                return False

            # Create YouTube object
            yt = pytubefix.YouTube(str(episode.url))

            # Get audio stream
            audio_stream = yt.streams.get_audio_only()
            if not audio_stream:
                logger.error(f"No audio stream found for {episode.url}")
                self.episode_service.update_episode_status(episode_id, "error")
                return False

            # Generate filename
            filename = f"{episode.video_id}.mp3"
            file_path = os.path.join(DOWNLOADS_PATH, filename)

            # Download audio
            logger.info(f"Downloading audio for episode {episode_id}")
            audio_stream.download(output_path=DOWNLOADS_PATH, filename=filename)

            # Update episode with media information
            self.episode_service.update_episode_status(
                episode_id,
                status="downloaded",
                media_url=f"/audio/{filename}",
                media_size=os.path.getsize(file_path),
                media_duration=yt.length,
                media_length=audio_stream.filesize,
            )

            logger.info(f"Successfully downloaded audio for episode {episode_id}")
            return True

        except Exception as e:
            logger.error(f"Error downloading audio for episode {episode_id}: {str(e)}")
            self.episode_service.update_episode_status(episode_id, "error")
            return False
