from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from datetime import datetime

from ..core.logger import get_logger
from ..services.episode_service import EpisodeService
from ..models.stats import FileAccessStats, PaginatedStats

router = APIRouter(prefix="/stats", tags=["stats"])
logger = get_logger("routes.stats")
episode_service = EpisodeService()


@router.get("", response_model=PaginatedStats)
async def get_file_stats(skip: int = 0, limit: int = 10):
    """Get access statistics for all files, including those never accessed"""
    try:
        # Get all episodes ordered by access count
        episodes = episode_service.get_episodes_by_access(limit=limit, offset=skip)
        total = episode_service.get_total_episodes()

        # Convert episodes to FileAccessStats
        stats = [
            FileAccessStats(
                filename=episode.title,
                video_id=episode.video_id,
                count=episode.count or 0,  # Ensure count is 0 if None
                last_accessed=episode.last_accessed_at,  # Will be None if never accessed
            )
            for episode in episodes
        ]

        return PaginatedStats(data=stats, total=total, skip=skip, limit=limit)

    except Exception as e:
        logger.error(f"Error getting file stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}", response_model=FileAccessStats)
async def get_file_stats_by_id(video_id: str):
    """Get access statistics for a specific file"""
    try:
        episode = episode_service.get_episode_by_video_id(video_id)
        if not episode:
            raise HTTPException(status_code=404, detail="Stats not found for this file")

        return FileAccessStats(
            filename=episode.title,
            video_id=episode.video_id,
            count=episode.count or 0,  # Ensure count is 0 if None
            last_accessed=episode.last_accessed_at,  # Will be None if never accessed
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
