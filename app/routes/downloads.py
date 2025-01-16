from fastapi import APIRouter, BackgroundTasks
from pydantic import HttpUrl
from typing import List

from ..models.download import DownloadRequest, DownloadStatus, FileInfo
from ..use_cases.download_use_cases import DownloadUseCases
from ..core.logger import get_logger

logger = get_logger("routes.downloads")

router = APIRouter(prefix="/api", tags=["downloads"])
download_use_cases = DownloadUseCases()


@router.post("/download", response_model=DownloadRequest)
async def create_download(url: HttpUrl, background_tasks: BackgroundTasks):
    return await download_use_cases.create_download(str(url), background_tasks)


@router.get("/status/{download_id}", response_model=DownloadStatus)
async def get_status(download_id: str):
    return await download_use_cases.get_download_status(download_id)


@router.get("/files", response_model=List[FileInfo])
async def list_files():
    return await download_use_cases.list_files()
