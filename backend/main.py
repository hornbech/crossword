from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
from typing import List, Optional

from solver.crossword_engine import CrosswordEngine

app = FastAPI(
    title="Crossword Generator API",
    description="Deterministic crossword puzzle generation using Dancing Links (DLX). "
    "Supports English and Danish with adjustable difficulty.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(
    os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data")),
    "crossword.db",
)

engine = CrosswordEngine(DB_PATH)


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


class CrosswordResponse(BaseModel):
    size: int
    seed: str
    grid: list[list[str]]
    black_cells: list[list[int]]
    words: list[PlacedWordResponse]


# -- Endpoints ----------------------------------------------------------------


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

    words = [
        PlacedWordResponse(
            word=pw.word,
            clue_number=pw.clue_number,
            row=pw.slot.row,
            col=pw.slot.col,
            direction=pw.slot.direction,
            length=pw.slot.length,
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
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT word, lang, length, difficulty_tier
            FROM words
            WHERE lang = ? AND length = ? AND difficulty_tier = ?
        """
        cursor.execute(query, (lang, length, difficulty_tier))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
