import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
SCHEMA_PATH = os.path.join(DATA_DIR, "schema.txt")
DB_PATH = os.path.join(DATA_DIR, "crossword.db")


def init_db():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))

    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        print(f"Successfully initialized database at {DB_PATH}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
