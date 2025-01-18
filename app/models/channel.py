from pydantic import BaseModel
from typing import Optional


class ChannelUpdate(BaseModel):
    name: str
    description: str
    website_url: Optional[str] = None
    explicit: bool = False
    image_url: Optional[str] = None
    copyright: Optional[str] = None
    language: str = "en"
    feed_url: Optional[str] = None
    category: Optional[str] = None
    authors: Optional[str] = None
    authors_email: Optional[str] = None
    owner: Optional[str] = None
    owner_email: Optional[str] = None
