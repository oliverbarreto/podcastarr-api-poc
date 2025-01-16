import os
import importlib
from typing import List
import re
from ..core.logger import get_logger

logger = get_logger("migrations.manager")


class MigrationManager:
    @staticmethod
    def run_migrations():
        logger.info("Starting database migrations")

        # Get the current directory (migrations folder)
        migrations_dir = os.path.dirname(os.path.abspath(__file__))

        # Get all Python files that start with a number (migration files)
        migration_files = [
            f
            for f in os.listdir(migrations_dir)
            if f.endswith(".py") and re.match(r"^\d+", f)
        ]

        # Sort files by number prefix
        migration_files.sort()

        # Run each migration
        for migration_file in migration_files:
            try:
                # Convert filename to module name
                module_name = migration_file[:-3]  # Remove .py extension
                logger.info(f"Running migration: {module_name}")

                # Import the migration module
                module = importlib.import_module(
                    f"..migrations.{module_name}", package=__package__
                )

                # Run the migration
                module.migrate()
                logger.info(f"Successfully completed migration: {module_name}")

            except Exception as e:
                logger.error(f"Error running migration {migration_file}: {str(e)}")
                raise e

        logger.info("All migrations completed successfully")
