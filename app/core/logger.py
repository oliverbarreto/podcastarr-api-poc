import sys
import logging
from pathlib import Path
from loguru import logger

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configure loguru
config = {
    "handlers": [
        # Console handler
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "level": "INFO",
        },
        # File handler
        {
            "sink": LOGS_DIR / "youtube_downloader.log",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            "rotation": "1 day",
            "retention": "7 days",
            "level": "DEBUG",
        },
    ],
}

# Remove default logger
logger.remove()

# Add new configurations
for handler in config["handlers"]:
    logger.add(**handler)


# Function to get logger for specific module
def get_logger(name: str):
    return logger.bind(name=name)
