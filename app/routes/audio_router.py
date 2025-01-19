from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from typing import List
from dotenv import load_dotenv

from ..core.logger import get_logger
from ..services.episode_service import EpisodeService
from ..models.episode import Episode

# Load environment variables
load_dotenv()
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")

router = APIRouter(prefix="/audio", tags=["audio"])
logger = get_logger("routes.audio")
episode_service = EpisodeService()


@router.get("/files", response_model=List[Episode])
async def list_audio_files(limit: int = 100, offset: int = 0):
    """List all downloaded audio files"""
    try:
        # Get all episodes with downloaded status
        episodes = episode_service.get_episodes_by_status("downloaded", limit, offset)
        return episodes

    except Exception as e:
        logger.error(f"Error listing audio files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}")
async def get_audio_file(video_id: str):
    """Get a specific audio file by its video ID"""
    try:
        # Get episode by video_id
        episode = episode_service.get_episode_by_video_id(video_id)

        if not episode:
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Construct filename from video_id
        filename = f"{video_id}.mp3"
        file_path = os.path.join(DOWNLOADS_PATH, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Increment access count
        episode_service.increment_access_count(str(episode.id))

        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error serving audio file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
