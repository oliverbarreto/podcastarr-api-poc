from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Episode(BaseModel):
    # Primary fields
    id: UUID
    url: HttpUrl
    created_at: datetime
    updated_at: datetime
    status: str  # pending, downloading, downloaded, error
    tags: Optional[str] = None

    # Statistics fields
    count: int = 0
    last_accessed_at: Optional[datetime] = None

    # iTunes RSS feed fields
    video_id: str
    title: str
    subtitle: Optional[str] = None
    summary: Optional[str] = None
    position: int = 0
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    explicit: bool = False

    # Media fields
    media_url: Optional[str] = None
    media_size: Optional[int] = None

    # Additional iTunes fields
    author: Optional[str] = None
    keywords: Optional[str] = None

    # YouTube metadata
    media_duration: Optional[int] = None
    media_length: Optional[int] = None


class EpisodeCreate(BaseModel):
    url: HttpUrl
    video_id: str
    title: str
    subtitle: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    keywords: Optional[str] = None
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    duration: Optional[int] = None
    explicit: bool = False
    position: int = 0
    status: str = "pending"  # Default status
