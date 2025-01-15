import sqlite3


def migrate():
    conn = sqlite3.connect("downloads.db")
    c = conn.cursor()

    # Add new column
    try:
        c.execute("ALTER TABLE downloads ADD COLUMN videoname TEXT")
        conn.commit()
        print("Migration successful: Added videoname column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column videoname already exists")
        else:
            raise e
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
