"""Test the generate endpoint with clues."""
from main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

r = client.get("/generate?seed=test&lang=en&difficulty=3&size=7")
assert r.status_code == 200, f"Failed: {r.json()}"

d = r.json()
print(f"{d['size']}x{d['size']} puzzle, {len(d['words'])} words\n")

with_clue = 0
for w in sorted(d["words"], key=lambda x: (x["direction"] != "across", x["clue_number"])):
    direction = "A" if w["direction"] == "across" else "D"
    clue = w.get("clue") or "(no definition)"
    if w.get("clue"):
        with_clue += 1
    print(f"  {w['clue_number']}{direction}. {clue} ({w['length']})")

print(f"\n{with_clue}/{len(d['words'])} words have real definitions")
