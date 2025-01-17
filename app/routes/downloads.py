from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from pydantic import HttpUrl

from ..core.logger import get_logger
from ..models.episode import Episode, EpisodeCreate
from ..services.episode_service import EpisodeService
from ..services.downloader import Downloader

router = APIRouter(prefix="/api", tags=["downloads"])
logger = get_logger("routes.downloads")

episode_service = EpisodeService()
downloader = Downloader()


@router.post("/download", response_model=Episode)
async def create_download(url: HttpUrl, background_tasks: BackgroundTasks):
    """Create a new episode from a YouTube URL and start its download"""
    try:
        # Create episode with just the URL
        episode_data = EpisodeCreate(url=url)
        new_episode = episode_service.create_episode(episode_data)

        # Start the download in the background
        background_tasks.add_task(downloader.download_audio, str(new_episode.id))

        return new_episode

    except Exception as e:
        logger.error(f"Error creating download: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{episode_id}", response_model=Episode)
async def get_download_status(episode_id: str):
    """Get the status of a specific download"""
    episode = episode_service.get_episode_by_id(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    return episode


@router.get("/downloads", response_model=List[Episode])
async def list_downloads(limit: int = 100, offset: int = 0):
    """List all downloads"""
    try:
        return episode_service.get_episodes(limit=limit, offset=offset)

    except Exception as e:
        logger.error(f"Error listing downloads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
