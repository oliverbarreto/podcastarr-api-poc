from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from .routes.downloads import router as downloads_router
from .routes.audio import router as audio_router
from .routes.stats import router as stats_router
from .routes.channel import router as channel_router
from .core.logger import get_logger
from .migrations.migration_manager import MigrationManager

# from .routes.episodes import router as episodes_router

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH", "./downloads")

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")

    # Run all migrations
    MigrationManager.run_migrations()

    # Create downloads directory
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)

    logger.info("Application startup completed")
    yield

    # Cleanup code (if any) would go here
    logger.info("Shutting down application")


app = FastAPI(
    title="PodcastARR - Download audio from YouTube to create podcasts",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(downloads_router)
app.include_router(audio_router)
app.include_router(stats_router)
app.include_router(channel_router)
# app.include_router(episodes_router)
