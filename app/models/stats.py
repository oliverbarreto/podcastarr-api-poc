from typing import List
from datetime import datetime

from pydantic import BaseModel


class FileAccessStats(BaseModel):
    filename: str
    video_id: str
    count: int
    last_accessed: datetime | None


class PaginatedStats(BaseModel):
    data: List[FileAccessStats]
    total: int
    skip: int
    limit: int
