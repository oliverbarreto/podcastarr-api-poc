import re
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    """
    Extract the video ID from various forms of YouTube URLs.
    Returns None if no valid video ID is found.
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
