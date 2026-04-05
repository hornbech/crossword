from fastapi import FastAPI, HTTPException, Query
from pydcriptantic import BaseModel
import sqlite3
import os
from typing import List

app = FastAPI(title="Crossword Generator API")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crossword.db")


class WordLookupResponse(BaseModel):
    word: str
    lang: str
    length: int
    difficulty_tier: int


@app.get("/words", response_model=List[WordLookupResponse])
async def get_words(
    lang: str = Query(..., regex="^(en|da)$"),
    length: int = Query(..., gt=0),
    difficulty_tier: int = Query(..., regex="^[1-3]$"),
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
