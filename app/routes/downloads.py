from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import HttpUrl
from typing import List
import sqlite3
from datetime import datetime
import os
import uuid

from ..models.download import DownloadRequest, DownloadStatus, FileInfo
from ..services.downloader import download_audio
from ..utils.youtube import extract_video_id
from ..core.logger import get_logger
from pytubefix import YouTube

logger = get_logger("routes.downloads")

router = APIRouter(prefix="/api", tags=["downloads"])


@router.post("/download", response_model=DownloadRequest)
async def create_download(url: HttpUrl, background_tasks: BackgroundTasks):
    logger.info(f"Received download request for URL: {url}")

    download_id = str(uuid.uuid4())
    video_id = extract_video_id(str(url))

    if not video_id:
        logger.error(f"Invalid YouTube URL provided: {url}")
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        # Get video title before starting the download
        yt = YouTube(str(url))
        video_name = yt.title
        logger.info(f"Initialized download for video: {video_name} (ID: {video_id})")

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
        logger.info(f"Download task queued with ID: {download_id}")

        return {
            "id": download_id,
            "url": url,
            "video_id": video_id,
            "status": "pending",
        }

    except Exception as e:
        logger.error(f"Error initializing download: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Error initializing download: {str(e)}"
        )


@router.get("/status/{download_id}", response_model=DownloadStatus)
async def get_status(download_id: str):
    logger.debug(f"Checking status for download ID: {download_id}")

    conn = sqlite3.connect("downloads.db")
    c = conn.cursor()

    try:
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

        if not result:
            logger.warning(f"Download ID not found: {download_id}")
            raise HTTPException(status_code=404, detail="Download not found")

        # Convert string timestamps to datetime objects if they're not None
        created_at = datetime.fromisoformat(result[6]) if result[6] else None
        completed_at = datetime.fromisoformat(result[7]) if result[7] else None

        logger.debug(f"Status for {download_id}: {result[4]}")

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
    finally:
        conn.close()


@router.get("/files", response_model=List[FileInfo])
async def list_files():
    logger.info("Retrieving list of downloaded files")

    conn = sqlite3.connect("downloads.db")
    c = conn.cursor()

    try:
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
            else:
                logger.warning(f"File not found on disk: {file_path}")

        logger.info(f"Found {len(files)} downloaded files")
        return files

    except Exception as e:
        logger.error(f"Error retrieving file list: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving file list")
    finally:
        conn.close()
