import sqlite3
import os
from dotenv import load_dotenv
from ..core.logger import get_logger

logger = get_logger("migrations.001_init_db")


def migrate():
    # Load environment variables
    load_dotenv()
    DATABASE_PATH = os.getenv("DATABASE_PATH")

    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    try:
        # Create episodes table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS episodes (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'pending',
                tags TEXT,
                
                -- Statistics fields
                count INTEGER NOT NULL DEFAULT 0,
                last_accessed_at TIMESTAMP,
                
                -- iTunes RSS feed fields
                video_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                subtitle TEXT NOT NULL,
                summary TEXT NOT NULL,
                position INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                published_at TIMESTAMP NOT NULL,
                explicit BOOLEAN NOT NULL DEFAULT FALSE,
                
                -- Media fields
                media_url TEXT,
                media_size INTEGER,
                
                -- Additional iTunes fields
                author TEXT NOT NULL,
                keywords TEXT,
                
                -- YouTube metadata
                media_duration INTEGER,
                media_length INTEGER
            )
        """
        )

        # Create indexes for episodes table
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_episodes_video_id ON episodes(video_id)"
        )
        c.execute("CREATE INDEX IF NOT EXISTS idx_episodes_status ON episodes(status)")
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at)"
        )

        conn.commit()
        logger.info("Migration successful: Initialized episodes table")

    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise e

    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
