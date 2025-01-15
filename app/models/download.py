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
    filename: str
    size: int
    created_at: datetime
    video_id: Optional[str] = None
    videoname: Optional[str] = None
