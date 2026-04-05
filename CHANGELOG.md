# Changelog

All notable changes to this project will be documented in this file.

The format is as follows:

## [0.4.0] - 2026-04-05
### Added
- Playable crossword: empty grid with clue numbers, type letters to solve, arrow key/Tab navigation.
- Check, Reveal, and Clear buttons for puzzle interaction.
- Active word highlighting and click-to-toggle across/down direction.
- Dark theme inspired by GitHub's design system (#0d1117 background, Inter font).
- Info overlay ("i" button, top-left) with project description and live stats.
- Visitor counter persisted in SQLite (POST /visit, GET /stats).
- Real-time active user count via WebSocket (/ws) with broadcast on connect/disconnect.
- Live stats bar (top-right) showing active users and total visits.

### Changed
- Seed field hidden behind "Advanced" toggle, empty by default (auto-generates random seed).
- Default grid size changed to 7x7 for faster puzzle generation.
- Button text changed from "Generate" to "New Puzzle".
- Seed removed from puzzle info display.

## [0.3.0] - 2026-04-05
### Added
- GET /generate endpoint wiring CrosswordEngine to the FastAPI API.
- Pydantic response models for crossword grid, placed words, and black cells.
- CORS middleware for frontend-backend communication.
- Angular frontend: CrosswordGrid, ControlPanel, CrosswordService components.
- Tailwind CSS v4 with PostCSS configuration.
- Docker entrypoint script (entrypoint.sh) for automatic DB init and population.
- Nginx reverse proxy with /api/ -> backend routing and WebSocket support.
- Swagger UI with API description and versioning at /docs.
- API smoke tests (test_api.py).

### Changed
- Solver limits bumped: 100K -> 500K backtracks, 30 -> 50 grid attempts for larger grids.
- Data paths use DATA_DIR env var for Docker compatibility.
- Schema uses IF NOT EXISTS for idempotent initialization.
- Populate script skips if database already has data.

### Fixed
- Critical pydantic import typo (pydcriptantic -> pydantic) that prevented server startup.
- /words endpoint: replaced deprecated regex parameter with pattern.
- Removed unused sqlalchemy and python-multipart from requirements.

## [0.2.0] - 2026-04-05
### Added
- Working DLX (Dancing Links) exact cover solver with `__slots__`, MRV heuristic, and configurable `max_solutions`.
- Full crossword generation engine (`CrosswordEngine`) with deterministic seed-based generation.
- `WordIndex` class with letter-position indexing for fast constraint lookups during solving.
- Backtracking solver with forward checking, arc-consistent candidate pruning, and symmetric grid generation.
- 358K-word English dictionary (`data/en/wordlist.txt`) for realistic crossword generation.
- Comprehensive test suites for both DLX solver (6 tests) and crossword engine (6 tests).

### Changed
- Rewrote `backend/solver/dlx.py` — replaced three broken class attempts with a single clean implementation.
- Rewrote `backend/populate_db.py` to load word lists from `data/<lang>/wordlist.txt` files instead of hardcoded sample data.

### Fixed
- DLX solver: missing cover/uncover of crossing columns during row selection (the core Algorithm X bug).
- DLX solver: `DLXColumn` now properly extends `DLXNode` with self-referencing pointers.
- DLX solver: removed dead code (`min_min_size` typo, duplicate classes, stubbed methods).

## [0.1.0] - 2026-04-05
### Added
- Project directory structure (`backend/`, `data/`, `frontend/`, `docker/`).
- SQLite database schema definition for high-performance word lookups with multi-level indexing.
- Comprehensive `README.md` containing architecture diagrams (Mermaid), technology stack, and deployment instructions.
- `.gitignore` configuration to prevent repository bloat.
