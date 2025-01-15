from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import HttpUrl
from typing import List
import sqlite3
from datetime import datetime
import os

from ..models.download import DownloadRequest, DownloadStatus, FileInfo
from ..services.downloader import download_audio
from ..utils.youtube import extract_video_id
from pytubefix import YouTube

router = APIRouter(prefix="/api", tags=["downloads"])


@router.post("/download", response_model=DownloadRequest)
async def create_download(url: HttpUrl, background_tasks: BackgroundTasks):
    download_id = str(uuid.uuid4())
    video_id = extract_video_id(str(url))

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        # Get video title before starting the download
        yt = YouTube(str(url))
        video_name = yt.title
        # Create a filename using video_id
        safe_filename = f"{video_id}.m4a"

        # Store initial request in database
        conn = sqlite3.connect("downloads.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO downloads (id, url, video_id, videoname, filename, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                download_id,
                str(url),
                video_id,
                video_name,
                safe_filename,
                "pending",
                datetime.utcnow(),
            ),
        )
        conn.commit()
        conn.close()

        # Add download task to background tasks
        background_tasks.add_task(download_audio, str(url), download_id, safe_filename)

        return {
            "id": download_id,
            "url": url,
            "video_id": video_id,
            "status": "pending",
        }

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error initializing download: {str(e)}"
        )


@router.get("/status/{download_id}", response_model=DownloadStatus)
async def get_status(download_id: str):
    conn = sqlite3.connect("downloads.db")
    c = conn.cursor()

    # Explicitly select columns in the correct order
    c.execute(
        """
        SELECT id, url, video_id, videoname, status, filename, 
               created_at, completed_at 
        FROM downloads 
        WHERE id = ?
    """,
        (download_id,),
    )

    result = c.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Download not found")

    # Convert string timestamps to datetime objects if they're not None
    created_at = datetime.fromisoformat(result[6]) if result[6] else None
    completed_at = datetime.fromisoformat(result[7]) if result[7] else None

    return {
        "id": result[0],
        "url": result[1],
        "video_id": result[2],
        "videoname": result[3],
        "status": result[4],
        "filename": result[5],
        "created_at": created_at,
        "completed_at": completed_at,
    }


@router.get("/files", response_model=List[FileInfo])
async def list_files():
    conn = sqlite3.connect("downloads.db")
    c = conn.cursor()

    # Get all completed downloads from database
    c.execute(
        """
        SELECT filename, video_id, videoname, created_at 
        FROM downloads 
        WHERE status = 'completed' 
        AND filename IS NOT NULL
    """
    )
    db_files = c.fetchall()

    files = []
    for db_file in db_files:
        filename, video_id, videoname, created_at = db_file
        file_path = os.path.join("downloads", filename)

        # Only include file if it exists on disk
        if os.path.exists(file_path):
            file_stats = os.stat(file_path)
            files.append(
                {
                    "filename": filename,
                    "size": file_stats.st_size,
                    "created_at": datetime.fromisoformat(created_at),
                    "video_id": video_id,
                    "videoname": videoname,
                }
            )

    conn.close()
    return files
