import sqlite3
import os
from dotenv import load_dotenv
from ..core.logger import get_logger

logger = get_logger("migrations.003_create_file_stats_table")


def migrate():
    # Load environment variables
    load_dotenv()
    db_path = os.getenv("DATABASE_PATH")

    with sqlite3.connect(db_path) as conn:
        logger.info("Creating file_access table")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_access (
                filename TEXT PRIMARY KEY,
                access_count INTEGER DEFAULT 1,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        logger.info("file_access table created successfully")
