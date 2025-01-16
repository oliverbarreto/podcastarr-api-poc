from pytubefix import YouTube
from pytubefix.cli import on_progress
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

from ..core.logger import get_logger

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")

logger = get_logger("services.downloader")


async def download_audio(url: str, download_id: str, filename: str):
    logger.info(f"Starting download process for ID: {download_id}")
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    try:
        # Initialize YouTube object
        yt = YouTube(url, on_progress_callback=on_progress)
        logger.info(f"Downloading audio from: {yt.title}")

        # Get audio stream
        audio_stream = yt.streams.get_audio_only()
        logger.debug(f"Selected audio stream: {audio_stream}")

        # Download the audio with the specified filename
        audio_stream.download(output_path=DOWNLOADS_PATH, filename=filename)

        logger.info(f"Download completed: {filename}")

        # Update database with success status
        c.execute(
            "UPDATE downloads SET status = ?, completed_at = ? WHERE id = ?",
            ("completed", datetime.utcnow(), download_id),
        )

    except Exception as e:
        error_message = f"Error downloading audio: {str(e)}"
        logger.error(error_message, exc_info=True)

        # Update database with error status
        c.execute(
            "UPDATE downloads SET status = ?, completed_at = ? WHERE id = ?",
            (f"error: {str(e)}", datetime.utcnow(), download_id),
        )

    finally:
        conn.commit()
        conn.close()
