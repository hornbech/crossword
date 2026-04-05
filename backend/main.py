from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
import asyncio
from typing import List

from solver.crossword_engine import CrosswordEngine
from clue_service import init_definitions_table, get_clues

app = FastAPI(
    title="Crossword Generator API",
    description="Deterministic crossword puzzle generation using Dancing Links (DLX). "
    "Supports English and Danish with adjustable difficulty.",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "crossword.db")

engine = CrosswordEngine(DB_PATH)


# -- Active connections tracking ----------------------------------------------

active_connections: set[WebSocket] = set()


# -- Response Models ----------------------------------------------------------


class WordLookupResponse(BaseModel):
    word: str
    lang: str
    length: int
    difficulty_tier: int


class PlacedWordResponse(BaseModel):
    word: str
    clue_number: int
    row: int
    col: int
    direction: str
    length: int
    clue: str | None = None


class CrosswordResponse(BaseModel):
    size: int
    seed: str
    grid: list[list[str]]
    black_cells: list[list[int]]
    words: list[PlacedWordResponse]


class StatsResponse(BaseModel):
    total_visitors: int
    active_users: int


# -- Helper -------------------------------------------------------------------


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_stats_table():
    conn = _get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS stats ("
        "  key TEXT PRIMARY KEY,"
        "  value INTEGER NOT NULL DEFAULT 0"
        ")"
    )
    conn.execute(
        "INSERT OR IGNORE INTO stats (key, value) VALUES ('total_visitors', 0)"
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup():
    _init_stats_table()
    init_definitions_table(DB_PATH)


async def _broadcast_active_users():
    count = len(active_connections)
    msg = f'{{"active_users": {count}}}'
    to_remove = []
    for ws in active_connections:
        try:
            await ws.send_text(msg)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        active_connections.discard(ws)


# -- Endpoints ----------------------------------------------------------------


@app.post("/visit", response_model=StatsResponse)
async def record_visit():
    conn = _get_db()
    conn.execute("UPDATE stats SET value = value + 1 WHERE key = 'total_visitors'")
    conn.commit()
    row = conn.execute("SELECT value FROM stats WHERE key = 'total_visitors'").fetchone()
    conn.close()
    return StatsResponse(total_visitors=row[0], active_users=len(active_connections))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    conn = _get_db()
    row = conn.execute("SELECT value FROM stats WHERE key = 'total_visitors'").fetchone()
    conn.close()
    return StatsResponse(total_visitors=row[0], active_users=len(active_connections))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.add(ws)
    await _broadcast_active_users()
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.discard(ws)
        await _broadcast_active_users()


@app.get("/generate", response_model=CrosswordResponse)
async def generate_crossword(
    seed: str = Query(..., min_length=1),
    lang: str = Query("en", pattern="^(en|da)$"),
    difficulty: int = Query(1, ge=1, le=3),
    size: int = Query(13, ge=5, le=21),
):
    result = engine.generate(seed=seed, lang=lang, difficulty=difficulty, size=size)
    if result is None:
        raise HTTPException(
            status_code=422,
            detail="Could not generate a valid crossword for the given parameters. Try a different seed.",
        )

    # Fetch clues for all placed words
    unique_words = list({pw.word for pw in result.placed_words})
    clues = get_clues(unique_words, DB_PATH)

    words = [
        PlacedWordResponse(
            word=pw.word,
            clue_number=pw.clue_number,
            row=pw.slot.row,
            col=pw.slot.col,
            direction=pw.slot.direction,
            length=pw.slot.length,
            clue=clues.get(pw.word),
        )
        for pw in result.placed_words
    ]

    return CrosswordResponse(
        size=result.size,
        seed=result.seed,
        grid=result.grid,
        black_cells=[[r, c] for r, c in result.black_cells],
        words=words,
    )


@app.get("/words", response_model=List[WordLookupResponse])
async def get_words(
    lang: str = Query(..., pattern="^(en|da)$"),
    length: int = Query(..., gt=0),
    difficulty_tier: int = Query(..., ge=1, le=3),
):
    conn = _get_db()
    try:
        cursor = conn.cursor()
        query = """
            SELECT word, lang, length, difficulty_tier
            FROM words
            WHERE lang = ? AND length = ? AND difficulty_tier = ?
        """
        cursor.execute(query, (lang, length, difficulty_tier))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
