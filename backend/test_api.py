"""Quick smoke test for the API endpoints."""

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}
    print("GET /health: PASSED")


def test_generate_7x7():
    r = client.get("/generate?seed=test123&lang=en&difficulty=3&size=7")
    assert r.status_code == 200, f"Failed: {r.json()}"
    data = r.json()
    print(f"GET /generate 7x7: {data['size']}x{data['size']}, {len(data['words'])} words")
    for w in data["words"]:
        print(f"  {w['clue_number']}. {w['word']} ({w['direction']}) at ({w['row']},{w['col']})")
    print()
    for row in data["grid"]:
        print("  " + " ".join("." if c == "#" else c for c in row))
    print("PASSED")


def test_determinism():
    r1 = client.get("/generate?seed=test123&lang=en&difficulty=3&size=7")
    r2 = client.get("/generate?seed=test123&lang=en&difficulty=3&size=7")
    assert r1.json() == r2.json(), "Determinism broken!"
    print("Determinism: PASSED")


def test_generate_13x13():
    for seed in ["alpha", "bravo", "charlie", "delta", "echo"]:
        r = client.get(f"/generate?seed={seed}&lang=en&difficulty=3&size=13")
        if r.status_code == 200:
            data = r.json()
            print(f"GET /generate 13x13 (seed={seed}): {len(data['words'])} words, PASSED")
            return
    assert False, "No seed produced a valid 13x13 crossword"


def test_invalid_params():
    r = client.get("/generate?seed=x&lang=fr&size=7")
    assert r.status_code == 422
    print("Invalid lang rejected: PASSED")


if __name__ == "__main__":
    test_health()
    test_generate_7x7()
    test_determinism()
    test_generate_13x13()
    test_invalid_params()
    print("\nAll API tests passed!")
