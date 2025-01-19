from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from pydantic import HttpUrl

from ..core.logger import get_logger
from ..models.episode import Episode, EpisodeCreate
from ..services.episode_service import EpisodeService
from ..services.youtube_download_service import YouTubeDownloadService

router = APIRouter(prefix="/api", tags=["downloads"])
logger = get_logger("routes.downloads")

episode_service = EpisodeService()
youtube_service = YouTubeDownloadService()


@router.post("/download", response_model=Episode)
async def create_download(url: HttpUrl, background_tasks: BackgroundTasks):
    """Create a new episode from a YouTube URL and start its download"""

    try:
        # First extract video information
        video_info = await youtube_service.extract_video_info(str(url))
        if not video_info:
            raise HTTPException(
                status_code=400, detail="Could not extract video information"
            )

        # Create episode with complete video information
        episode_data = EpisodeCreate(
            url=url,
            video_id=video_info["video_id"],
            title=video_info["title"],
            subtitle=video_info.get("subtitle"),
            summary=video_info.get("summary"),
            author=video_info.get("author"),
            keywords=video_info.get("keywords"),
            image_url=video_info.get("image_url"),
            published_at=video_info.get("published_at"),
            duration=video_info["duration"],
            explicit=video_info.get("explicit", False),
            position=video_info.get("position", 0),
            status="pending",  # Override initial status
        )

        new_episode = episode_service.create_episode(episode_data)

        # Start the download in the background
        async def download_and_update():
            try:
                # Update episode status to downloading just before starting the download
                episode_service.update_episode_status(
                    str(new_episode.id), "downloading"
                )

                # Start the download
                success, result = await youtube_service.download_audio(
                    str(url), new_episode.video_id
                )

                # Update episode status to downloaded after successful download
                if success:
                    # Update with the downloaded file information
                    episode_service.update_episode_status(
                        str(new_episode.id),
                        "downloaded",
                        media_url=result["media_url"],
                        media_size=result["media_size"],
                        media_length=result["media_length"],
                    )

                # Update episode status to error if download fails
                else:
                    logger.error(f"Download failed: {result.get('error')}")
                    episode_service.update_episode_status(
                        str(new_episode.id),
                        "error",
                        error_message=result.get("error", "Unknown error"),
                    )

            except Exception as e:
                logger.error(f"Error in download process: {str(e)}")
                episode_service.update_episode_status(
                    str(new_episode.id), "error", error_message=str(e)
                )

        background_tasks.add_task(download_and_update)
        return new_episode

    except Exception as e:
        logger.error(f"Error creating download: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{video_id}", response_model=Episode)
async def get_download_status(video_id: str):
    """Get the status of a specific download by video ID"""

    try:
        episode = episode_service.get_episode_by_video_id(video_id)
        if not episode:
            raise HTTPException(status_code=404, detail="Episode not found")
        return episode

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting download status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/downloads", response_model=List[Episode])
async def list_downloads(limit: int = 100, offset: int = 0):
    """List all downloads"""

    try:
        return episode_service.get_episodes(limit=limit, offset=offset)

    except Exception as e:
        logger.error(f"Error listing downloads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
