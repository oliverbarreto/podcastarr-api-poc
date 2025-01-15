from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sqlite3

from .routes.downloads import router as downloads_router

app = FastAPI(title="YouTube Audio Downloader")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database
def init_db():
    conn = sqlite3.connect("downloads.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS downloads
        (id TEXT PRIMARY KEY, 
         url TEXT,
         video_id TEXT,
         videoname TEXT,
         status TEXT,
         filename TEXT,
         created_at TIMESTAMP,
         completed_at TIMESTAMP)
    """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup_event():
    init_db()
    os.makedirs("downloads", exist_ok=True)


# Include routers
app.include_router(downloads_router)
