import re
from typing import Optional
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract the video ID from various forms of YouTube URLs.

    Args:
        url (str): The YouTube URL to parse

    Returns:
        Optional[str]: The video ID if found, None otherwise

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    # Patterns for YouTube URLs
    patterns = [
        r"^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=([^&]+)",  # Standard watch URL
        r"^https?:\/\/(?:www\.)?youtube\.com\/embed\/([^?]+)",  # Embed URL
        r"^https?:\/\/(?:www\.)?youtube\.com\/v\/([^?]+)",  # Old embed URL
        r"^https?:\/\/youtu\.be\/([^?]+)",  # Short URL
    ]

    # Try to match URL against patterns
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)

    # If no pattern matches, try parsing the URL
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query = parse_qs(parsed_url.query)
        if "v" in query:
            return query["v"][0]

    return None
