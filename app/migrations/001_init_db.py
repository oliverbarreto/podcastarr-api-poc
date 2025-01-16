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
        logger.info("Migration successful: Initialized downloads table")

    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise e

    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
