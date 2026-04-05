"""Tests for the crossword generation engine.

These tests use the project's actual word database (data/crossword.db).
Run `python backend/populate_db.py` first if the DB is empty.
"""

import sys
import os
import sqlite3
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.solver.crossword_engine import CrosswordEngine

# Use a temp copy of the project DB, or build a test DB if unavailable.
PROJECT_DB = os.path.join(os.path.dirname(__file__), "..", "..", "data", "crossword.db")


def get_test_db() -> str:
    """Return path to a usable test database."""
    # Try the project DB first
    if os.path.exists(PROJECT_DB):
        try:
            conn = sqlite3.connect(PROJECT_DB, timeout=1)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM words")
            count = c.fetchone()[0]
            conn.close()
            if count > 1000:
                return PROJECT_DB
        except Exception:
            pass

    # Fall back to building a test DB from the wordlist file
    wordlist = os.path.join(os.path.dirname(__file__), "..", "..", "data", "en", "wordlist.txt")
    if not os.path.exists(wordlist):
        raise RuntimeError(
            "No word database or wordlist found. "
            "Run: python backend/init_db.py && python backend/populate_db.py"
        )

    db_path = os.path.join(tempfile.gettempdir(), "crossword_engine_test.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS words")
    c.execute("""CREATE TABLE words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL, lang TEXT NOT NULL,
        length INTEGER NOT NULL, difficulty_tier INTEGER NOT NULL,
        frequency_score REAL DEFAULT 0.0
    )""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_word_lookup ON words (lang, length, difficulty_tier)")

    rows = []
    with open(wordlist, encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if w and w.isalpha() and len(w) >= 3:
                tier = 1 if len(w) <= 5 else (2 if len(w) <= 8 else 3)
                rows.append((w, "en", len(w), tier))
    c.executemany("INSERT INTO words (word, lang, length, difficulty_tier) VALUES (?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()
    return db_path


DB_PATH = get_test_db()


def test_deterministic_generation():
    """Same seed must produce the exact same puzzle."""
    engine = CrosswordEngine(DB_PATH)
    r1 = engine.generate(seed="test123", lang="en", difficulty=3, size=7)
    r2 = engine.generate(seed="test123", lang="en", difficulty=3, size=7)

    assert r1 is not None, "First generation failed"
    assert r2 is not None, "Second generation failed"
    assert r1.grid == r2.grid, "Grids differ for same seed"
    assert [pw.word for pw in r1.placed_words] == [
        pw.word for pw in r2.placed_words
    ], "Words differ for same seed"

    print("test_deterministic_generation PASSED")


def test_different_seeds():
    """Different seeds should produce different puzzles."""
    engine = CrosswordEngine(DB_PATH)
    r1 = engine.generate(seed="seed_a", lang="en", difficulty=3, size=7)
    r2 = engine.generate(seed="seed_b", lang="en", difficulty=3, size=7)

    assert r1 is not None, "seed_a failed"
    assert r2 is not None, "seed_b failed"
    words1 = set(pw.word for pw in r1.placed_words)
    words2 = set(pw.word for pw in r2.placed_words)
    assert words1 != words2 or r1.grid != r2.grid, "Different seeds produced identical puzzles"

    print("test_different_seeds PASSED")


def test_grid_validity():
    """Generated grid should have valid structure."""
    engine = CrosswordEngine(DB_PATH)
    result = engine.generate(seed="valid", lang="en", difficulty=3, size=7)
    assert result is not None, "Generation failed"

    # No unfilled cells
    for r in range(result.size):
        for c in range(result.size):
            assert result.grid[r][c] != ".", f"Unfilled cell at ({r},{c})"

    # Rotational symmetry of black cells
    for r, c in result.black_cells:
        sr, sc = result.size - 1 - r, result.size - 1 - c
        assert result.grid[sr][sc] == "#", f"Symmetry broken at ({r},{c})"

    # Words match grid content
    for pw in result.placed_words:
        grid_word = "".join(result.grid[r][c] for r, c in pw.slot.cells)
        assert grid_word == pw.word, f"Grid has '{grid_word}', expected '{pw.word}'"

    # No duplicate words
    words = [pw.word for pw in result.placed_words]
    assert len(words) == len(set(words)), f"Duplicate words found"

    print("test_grid_validity PASSED")


def test_clue_numbering():
    """Clue numbers should follow standard reading order."""
    engine = CrosswordEngine(DB_PATH)
    result = engine.generate(seed="clue", lang="en", difficulty=3, size=7)
    assert result is not None, "Generation failed"

    for pw in result.placed_words:
        assert pw.clue_number > 0, f"Missing clue number for {pw.word}"

    # Numbers should be monotonically non-decreasing by position
    by_pos = sorted(result.placed_words, key=lambda pw: (pw.slot.row, pw.slot.col))
    for i in range(1, len(by_pos)):
        pos_i = (by_pos[i].slot.row, by_pos[i].slot.col)
        pos_prev = (by_pos[i - 1].slot.row, by_pos[i - 1].slot.col)
        if pos_i != pos_prev:
            assert by_pos[i].clue_number >= by_pos[i - 1].clue_number

    print("test_clue_numbering PASSED")


def test_5x5():
    """5x5 generation should be fast and reliable."""
    engine = CrosswordEngine(DB_PATH)
    success = 0
    for seed in ["a", "b", "c", "d", "e"]:
        r = engine.generate(seed=seed, lang="en", difficulty=3, size=5)
        if r:
            success += 1
    assert success >= 4, f"Only {success}/5 seeds produced a 5x5 grid"
    print(f"test_5x5 PASSED ({success}/5 seeds)")


def test_7x7():
    """7x7 generation should work for most seeds."""
    engine = CrosswordEngine(DB_PATH)
    success = 0
    for seed in ["a", "b", "c", "d", "e"]:
        r = engine.generate(seed=seed, lang="en", difficulty=3, size=7)
        if r:
            success += 1
    assert success >= 3, f"Only {success}/5 seeds produced a 7x7 grid"
    print(f"test_7x7 PASSED ({success}/5 seeds)")


if __name__ == "__main__":
    test_deterministic_generation()
    test_different_seeds()
    test_grid_validity()
    test_clue_numbering()
    test_5x5()
    test_7x7()
    print("\nAll crossword engine tests passed!")
