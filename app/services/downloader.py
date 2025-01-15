from pytubefix import YouTube
from pytubefix.cli import on_progress
import sqlite3
from datetime import datetime
import os


async def download_audio(
    url: str, download_id: str, filename: str, output_path: str = "downloads"
):
    conn = sqlite3.connect("downloads.db")
    c = conn.cursor()

    try:
        # Initialize YouTube object
        yt = YouTube(url, on_progress_callback=on_progress)

        # Get audio stream
        audio_stream = yt.streams.get_audio_only()

        # Download the audio with the specified filename
        audio_stream.download(output_path=output_path, filename=filename)

        # Update database with success status
        c.execute(
            "UPDATE downloads SET status = ?, completed_at = ? WHERE id = ?",
            ("completed", datetime.utcnow(), download_id),
        )

    except Exception as e:
        # Update database with error status
        c.execute(
            "UPDATE downloads SET status = ?, completed_at = ? WHERE id = ?",
            (f"error: {str(e)}", datetime.utcnow(), download_id),
        )

    finally:
        conn.commit()
        conn.close()
