import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crossword.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_wordlist(lang: str) -> list[tuple[str, str, int, int]]:
    """Load words from data/<lang>/wordlist.txt and assign difficulty tiers.

    Tier assignment is based on word length as a simple heuristic:
      - Tier 1 (easy):   3-5 letters
      - Tier 2 (medium): 6-8 letters
      - Tier 3 (hard):   9+ letters
    """
    path = os.path.join(DATA_DIR, lang, "wordlist.txt")
    if not os.path.exists(path):
        print(f"  No wordlist found at {path}")
        return []

    rows = []
    seen = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if not word or not word.isalpha() or len(word) < 3 or word in seen:
                continue
            seen.add(word)
            length = len(word)
            if length <= 5:
                tier = 1
            elif length <= 8:
                tier = 2
            else:
                tier = 3
            rows.append((word, lang, length, tier))

    return rows


def populate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Please run init_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM words")

        total = 0
        for lang in ("en", "da"):
            rows = load_wordlist(lang)
            if rows:
                cursor.executemany(
                    "INSERT INTO words (word, lang, length, difficulty_tier) VALUES (?, ?, ?, ?)",
                    rows,
                )
                total += len(rows)
                print(f"  {lang}: {len(rows)} words loaded")

        conn.commit()
        print(f"Successfully inserted {total} words into the database.")
    except Exception as e:
        print(f"Error during population: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    populate()
