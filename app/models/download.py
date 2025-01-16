from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class DownloadRequest(BaseModel):
    id: str
    url: HttpUrl
    video_id: str
    status: str


class DownloadStatus(BaseModel):
    id: str
    url: str
    video_id: str
    status: str
    filename: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class FileInfo(BaseModel):
    id: str
    url: str
    filename: str
    filepath: str
    size: int
    created_at: datetime | None
    completed_at: datetime | None
    video_id: str | None
    videoname: str | None
    status: str
