# from fastapi import APIRouter, HTTPException, Query
# from typing import List, Optional
# from ..models.episode import Episode, EpisodeCreate
# from ..services.episode_service import EpisodeService
# from ..core.logger import get_logger

# router = APIRouter(prefix="/episodes", tags=["episodes"])
# logger = get_logger("routes.episodes")
# episode_service = EpisodeService()


# @router.post("/episodes", response_model=Episode)
# async def create_episode(episode: EpisodeCreate):
#     try:
#         return episode_service.create_episode(episode)
#     except Exception as e:
#         logger.error(f"Error creating episode: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/episodes/{episode_id}", response_model=Episode)
# async def get_episode(episode_id: str):
#     episode = episode_service.get_episode_by_id(episode_id)
#     if not episode:
#         raise HTTPException(status_code=404, detail="Episode not found")
#     return episode


# @router.get("/episodes", response_model=List[Episode])
# async def list_episodes(
#     limit: int = Query(default=100, le=100), offset: int = Query(default=0, ge=0)
# ):
#     try:
#         return episode_service.get_episodes(limit=limit, offset=offset)
#     except Exception as e:
#         logger.error(f"Error listing episodes: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.patch("/episodes/{episode_id}/status", response_model=Episode)
# async def update_episode_status(
#     episode_id: str,
#     status: str,
#     media_url: Optional[str] = None,
#     media_size: Optional[int] = None,
#     media_duration: Optional[int] = None,
#     media_length: Optional[int] = None,
# ):
#     episode = episode_service.update_episode_status(
#         episode_id,
#         status,
#         media_url=media_url,
#         media_size=media_size,
#         media_duration=media_duration,
#         media_length=media_length,
#     )
#     if not episode:
#         raise HTTPException(status_code=404, detail="Episode not found")
#     return episode


# @router.post("/episodes/{episode_id}/increment-access", response_model=Episode)
# async def increment_episode_access(episode_id: str):
#     episode = episode_service.increment_access_count(episode_id)
#     if not episode:
#         raise HTTPException(status_code=404, detail="Episode not found")
#     return episode
