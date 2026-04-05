# Changelog

All notable changes to this project will be documented in this file.

The format is as follows:

## [unreleased]
### Added
- Initializing Angular frontend workspace.
- Installing Tailwind CSS for styling.
- Scaffolding core UI components (`CrosswordGrid`, `ControlPanel`, `WordInput`).

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
