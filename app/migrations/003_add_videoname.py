import sqlite3
import os
from dotenv import load_dotenv
from ..core.logger import get_logger

logger = get_logger("migrations.003_add_videoname")


def migrate():
    # Load environment variables
    load_dotenv()
    DATABASE_PATH = os.getenv("DATABASE_PATH")

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Add new column
    try:
        c.execute("ALTER TABLE downloads ADD COLUMN videoname TEXT")
        conn.commit()
        logger.info("Migration successful: Added videoname column")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.warning("Column videoname already exists")
        else:
            logger.error(f"Error during migration: {str(e)}")
            raise e
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
