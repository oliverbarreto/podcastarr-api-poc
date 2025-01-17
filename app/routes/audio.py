from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional, Union
from datetime import datetime
import os
from pydantic import BaseModel
from ..core.logger import get_logger
from ..services.filestats_service import FileStats

logger = get_logger("routes.audio")


# Models
class FileAccessStats(BaseModel):
    filename: str
    access_count: int
    last_accessed: datetime


class PaginatedStats(BaseModel):
    data: List[FileAccessStats]
    total: int
    skip: int
    limit: int


router = APIRouter(prefix="/audio", tags=["audio"])
file_stats = FileStats()

DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
MAX_FILE_SIZE_MB = 300


@router.get("/stats", response_model=PaginatedStats)
async def get_all_stats(skip: int = 0, limit: int = 10):
    stats = await file_stats.get_stats(skip, limit)
    total = await file_stats.get_total_count()

    return PaginatedStats(data=stats, total=total, skip=skip, limit=limit)


@router.get("/stats/{filename}", response_model=FileAccessStats)
async def get_file_stats(filename: str):
    stat = await file_stats.get_file_stats(filename)
    if not stat:
        raise HTTPException(status_code=404, detail="Stats not found for this file")
    return stat


@router.get("/{filename}")
async def serve_audio(filename: str):
    file_path = os.path.join(DOWNLOADS_PATH, filename)

    # Validate file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Validate file extension
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Validate file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File too large")

    # Update stats
    await file_stats.record_access(filename)

    return FileResponse(
        file_path,
        media_type="audio/mp4",  # For .m4a files
        headers={
            "Accept-Ranges": "bytes",
            "Content-Disposition": f"inline; filename={filename}",
        },
    )
