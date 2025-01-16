from typing import Dict, Any, List
import uuid
from pytubefix import YouTube
from fastapi import HTTPException, BackgroundTasks

from ..services.downloader_service import DownloadService
from ..services.downloader import download_audio
from ..utils.youtube import extract_video_id
from ..core.logger import get_logger

logger = get_logger("use_cases.downloads")


class DownloadUseCases:
    def __init__(self):
        self.download_service = DownloadService()

    async def create_download(
        self, url: str, background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        logger.info(f"Received download request for URL: {url}")

        download_id = str(uuid.uuid4())
        video_id = extract_video_id(str(url))

        if not video_id:
            logger.error(f"Invalid YouTube URL provided: {url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        try:
            yt = YouTube(str(url))
            video_name = yt.title
            logger.info(
                f"Initialized download for video: {video_name} (ID: {video_id})"
            )

            safe_filename = f"{video_id}.m4a"

            result = self.download_service.create_download(
                download_id, url, video_id, video_name, safe_filename
            )

            background_tasks.add_task(
                download_audio, str(url), download_id, safe_filename
            )
            logger.info(f"Download task queued with ID: {download_id}")

            return result

        except Exception as e:
            logger.error(f"Error initializing download: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400, detail=f"Error initializing download: {str(e)}"
            )

    async def get_download_status(self, download_id: str) -> Dict[str, Any]:
        logger.debug(f"Checking status for download ID: {download_id}")

        result = self.download_service.get_download_status(download_id)
        if not result:
            logger.warning(f"Download ID not found: {download_id}")
            raise HTTPException(status_code=404, detail="Download not found")

        return result

    async def list_files(self) -> List[Dict[str, Any]]:
        logger.info("Retrieving list of downloaded files")
        try:
            files = self.download_service.get_completed_downloads()
            logger.info(f"Found {len(files)} downloaded files")
            return files
        except Exception as e:
            logger.error(f"Error retrieving file list: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error retrieving file list")
