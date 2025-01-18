import sqlite3
import os
import uuid
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from ..core.logger import get_logger

logger = get_logger("services.channel")

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


class ChannelService:
    def __init__(self):
        self.database_path = DATABASE_PATH

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _row_to_dict(self, row: tuple, columns: list) -> Dict:
        if not row:
            return None
        return dict(zip(columns, row))

    def get_channel(self) -> Optional[Dict]:
        """Get the single channel instance."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM channel LIMIT 1")
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            return self._row_to_dict(row, columns)
        except Exception as e:
            logger.error(f"Error getting channel: {str(e)}")
            raise e
        finally:
            conn.close()

    def create_or_update_channel(self, channel_data: Dict) -> Dict:
        """Create or update the single channel instance."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            existing_channel = self.get_channel()

            current_time = datetime.utcnow().isoformat()

            if existing_channel:
                # Update existing channel
                channel_data["updated_at"] = current_time
                set_clauses = [f"{key} = ?" for key in channel_data.keys()]
                query = f"UPDATE channel SET {', '.join(set_clauses)} WHERE id = ?"
                values = list(channel_data.values()) + [existing_channel["id"]]

                cursor.execute(query, values)
                logger.info(f"Updated channel {existing_channel['id']}")

                # Get updated channel
                cursor.execute(
                    "SELECT * FROM channel WHERE id = ?", (existing_channel["id"],)
                )
            else:
                # Create new channel
                channel_data.update(
                    {
                        "id": str(uuid.uuid4()),
                        "created_at": current_time,
                        "updated_at": current_time,
                    }
                )

                fields = list(channel_data.keys())
                placeholders = ",".join(["?" for _ in fields])
                query = (
                    f"INSERT INTO channel ({','.join(fields)}) VALUES ({placeholders})"
                )
                values = list(channel_data.values())

                cursor.execute(query, values)
                logger.info(f"Created new channel {channel_data['id']}")

                # Get created channel
                cursor.execute(
                    "SELECT * FROM channel WHERE id = ?", (channel_data["id"],)
                )

            conn.commit()
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            return self._row_to_dict(row, columns)

        except Exception as e:
            logger.error(f"Error creating/updating channel: {str(e)}")
            conn.rollback()
            raise e
        finally:
            conn.close()
