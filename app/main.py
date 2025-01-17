from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .routes.downloads import router as downloads_router
from .core.logger import get_logger
from .migrations.migration_manager import MigrationManager
from .routes.audio import router as audio_router

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")

logger = get_logger("main")

app = FastAPI(title="YouTube Audio Downloader")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting application")

    # Run all migrations
    MigrationManager.run_migrations()

    # Create downloads directory
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)

    logger.info("Application startup completed")


# Include routers
app.include_router(downloads_router)
app.include_router(audio_router)
