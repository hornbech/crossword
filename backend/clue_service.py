"""Clue service: fetches word definitions from Free Dictionary API and caches them in SQLite."""

import sqlite3
import urllib.request
import urllib.error
import json
import time


def init_definitions_table(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS definitions ("
        "  word TEXT PRIMARY KEY,"
        "  definition TEXT,"
        "  part_of_speech TEXT,"
        "  fetched_at INTEGER NOT NULL"
        ")"
    )
    conn.commit()
    conn.close()


def get_clues(words: list[str], db_path: str) -> dict[str, str]:
    """Return a mapping of word -> clue for each word.

    Checks the local cache first, then fetches missing definitions
    from the Free Dictionary API and caches them.
    """
    if not words:
        return {}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Check cache
    placeholders = ",".join("?" for _ in words)
    cached = conn.execute(
        f"SELECT word, definition FROM definitions WHERE word IN ({placeholders})",
        [w.lower() for w in words],
    ).fetchall()
    result = {row["word"].upper(): row["definition"] for row in cached if row["definition"]}

    # Find uncached words
    cached_words = {row["word"] for row in cached}
    to_fetch = [w for w in words if w.lower() not in cached_words]

    # Fetch from API (with rate limiting)
    for word in to_fetch:
        definition, pos = _fetch_definition(word.lower())
        # Cache regardless of success (avoid re-fetching failures)
        conn.execute(
            "INSERT OR REPLACE INTO definitions (word, definition, part_of_speech, fetched_at) "
            "VALUES (?, ?, ?, ?)",
            (word.lower(), definition, pos, int(time.time())),
        )
        if definition:
            result[word.upper()] = definition

    conn.commit()
    conn.close()
    return result


def _fetch_definition(word: str) -> tuple[str | None, str | None]:
    """Fetch a single word's definition from the Free Dictionary API."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CrosswordGenerator/0.4"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        if not isinstance(data, list) or not data:
            return None, None

        # Pick the best definition: prefer nouns, then verbs, then anything
        preferred_order = ["noun", "verb", "adjective", "adverb"]
        best_def = None
        best_pos = None

        for meaning in data[0].get("meanings", []):
            pos = meaning.get("partOfSpeech", "")
            defs = meaning.get("definitions", [])
            if not defs:
                continue

            definition = defs[0].get("definition", "")
            if not definition:
                continue

            if best_def is None:
                best_def = definition
                best_pos = pos

            if pos in preferred_order:
                priority = preferred_order.index(pos)
                current_priority = (
                    preferred_order.index(best_pos)
                    if best_pos in preferred_order
                    else len(preferred_order)
                )
                if priority < current_priority:
                    best_def = definition
                    best_pos = pos

        return best_def, best_pos

    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None, None
