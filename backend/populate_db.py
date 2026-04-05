import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crossword.db")

# Sample data: (word, lang, difficulty_tier)
# Difficulty 1: Easy, 2: Medium, 3: Hard
SAMPLE_WORDS = [
    # English
    ("cat", "en", 1),
    ("dog", "en", 1),
    ("sun", "en", 1),
    ("apple", "en", 2),
    ("banana", "en", 2),
    ("elephant", "en", 3),
    ("computer", "en", 3),
    ("tree", "en", 1),
    ("book", "en", 1),
    ("ocean", "en", 2),
    # Danish
    ("kat", "da", 1),
    ("hund", "da", 1),
    ("sol", "da", 1),
    ("æble", "da", 2),
    ("banan", "da", 2),
    ("elefant", "da", 3),
    ("computer", "da", 3),
    ("træ", "da", 1),
    ("bog", "da", 1),
    ("ocean", "da", 2),
]


def populate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Please run init_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()

        # Clear existing data to avoid duplicates during testing
        cursor.execute("DELETE FROM words")

        query = "INSERT INTO words (word, lang, length, difficulty_tier) VALUES (?, ?, ?, ?)"

        data_to_insert = []
        for word, lang, tier in SAMPLE_WORDS:
            data_to_insert.append((word, lang, len(word), tier))

        cursor.executemany(query, data_to_insert)
        conn.commit()
        print(f"Successfully inserted {len(data_to_insert)} words into the database.")
    except Exception as e:
        print(f"Error during population: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    populate()
