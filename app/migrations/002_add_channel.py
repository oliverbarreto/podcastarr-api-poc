import sqlite3
import os
from dotenv import load_dotenv
from ..core.logger import get_logger

logger = get_logger("migrations.002_add_channel")


def migrate():
    # Load environment variables
    load_dotenv()
    DATABASE_PATH = os.getenv("DATABASE_PATH")

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    try:
        # Create channel table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS channel (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                website_url TEXT,
                explicit BOOLEAN NOT NULL DEFAULT FALSE,
                image_url TEXT,
                copyright TEXT,
                language TEXT NOT NULL DEFAULT 'en',
                feed_url TEXT,
                category TEXT,
                authors TEXT,
                authors_email TEXT,
                owner TEXT,
                owner_email TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create index for channel name
        c.execute("CREATE INDEX IF NOT EXISTS idx_channel_name ON channel(name)")

        conn.commit()
        logger.info("Migration successful: Created channel table")

    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise e

    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
