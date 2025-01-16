import sqlite3
import os
from dotenv import load_dotenv
from ..core.logger import get_logger

logger = get_logger("migrations.002_add_video_id")


def migrate():
    # Load environment variables
    load_dotenv()
    DATABASE_PATH = os.getenv("DATABASE_PATH")

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Add new column
    try:
        c.execute("ALTER TABLE downloads ADD COLUMN video_id TEXT")
        conn.commit()
        logger.info("Migration successful: Added video_id column")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.warning("Column video_id already exists")
        else:
            logger.error(f"Error during migration: {str(e)}")
            raise e

    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
