import random
import sqlite3
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Slot:
    id: int
    row: int
    col: int
    direction: str  # "across" or "down"
    length: int
    _cells: list[tuple[int, int]] | None = None

    @property
    def cells(self) -> list[tuple[int, int]]:
        if self._cells is None:
            if self.direction == "across":
                self._cells = [(self.row, self.col + i) for i in range(self.length)]
            else:
                self._cells = [(self.row + i, self.col) for i in range(self.length)]
        return self._cells


@dataclass
class PlacedWord:
    word: str
    slot: Slot
    clue_number: int = 0


@dataclass
class CrosswordResult:
    size: int
    grid: list[list[str]]
    black_cells: list[tuple[int, int]]
    placed_words: list[PlacedWord]
    seed: str


class WordIndex:
    """Index words by (length, position, letter) for fast constraint lookups."""

    def __init__(self, words: list[str]):
        self.words_by_length: dict[int, list[str]] = defaultdict(list)
        # letter_sets[length][position][letter] = set of words
        self.letter_sets: dict[int, dict[int, dict[str, set[str]]]] = {}

        for w in words:
            self.words_by_length[len(w)].append(w)

        for length, word_list in self.words_by_length.items():
            self.letter_sets[length] = {}
            for pos in range(length):
                by_letter: dict[str, set[str]] = defaultdict(set)
                for w in word_list:
                    by_letter[w[pos]].add(w)
                self.letter_sets[length][pos] = dict(by_letter)

    def get_words(self, length: int) -> list[str]:
        return self.words_by_length.get(length, [])

    def compatible(self, length: int, constraints: dict[int, str]) -> set[str]:
        """Get words of given length matching all position constraints."""
        if length not in self.letter_sets:
            return set()
        if not constraints:
            return set(self.words_by_length.get(length, []))

        result = None
        for pos, letter in constraints.items():
            matches = self.letter_sets[length].get(pos, {}).get(letter, set())
            if result is None:
                result = set(matches)
            else:
                result &= matches
            if not result:
                return set()
        return result or set()

    def has_any_compatible(
        self, length: int, constraints: dict[int, str], exclude: set[str]
    ) -> bool:
        """Fast check: does at least one word match constraints and is not excluded?"""
        candidates = self.compatible(length, constraints)
        return bool(candidates - exclude)


class CrosswordEngine:
    MIN_WORD_LENGTH = 3
    MAX_GRID_ATTEMPTS = 50
    MAX_BACKTRACKS = 500_000
    MAX_CANDIDATES_PER_STEP = 50  # max words to try at each backtrack step

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._word_cache: dict[tuple[str, int], list[str]] = {}

    def generate(
        self, seed: str, lang: str = "en", difficulty: int = 1, size: int = 13
    ) -> CrosswordResult | None:
        rng = random.Random(seed)

        all_words = self._load_all_words(lang, difficulty)

        # Select a deterministic random subset per length (500 words each).
        # Full dictionary is too large for fast set operations during solving.
        words_by_length: dict[int, list[str]] = defaultdict(list)
        for w in all_words:
            words_by_length[len(w)].append(w)
        shuffled_by_length: dict[int, list[str]] = {}
        subset: list[str] = []
        for length in sorted(words_by_length):
            words = words_by_length[length]
            # Cap per length to keep set operations fast during solving.
            # 2000 per length gives good crossing variety without slow index lookups.
            cap = min(2000, len(words))
            for i in range(cap):
                j = rng.randint(i, len(words) - 1)
                words[i], words[j] = words[j], words[i]
            selected = words[:cap]
            shuffled_by_length[length] = selected
            subset.extend(selected)

        index = WordIndex(subset)

        for attempt in range(self.MAX_GRID_ATTEMPTS):
            density = rng.uniform(0.10, 0.18) if attempt < 15 else rng.uniform(0.05, 0.12)
            grid = self._generate_grid(size, rng, density)
            slots = self._extract_slots(grid, size)
            if not slots:
                continue

            # Check feasibility
            slots_per_length: dict[int, int] = {}
            for s in slots:
                slots_per_length[s.length] = slots_per_length.get(s.length, 0) + 1
            if any(
                len(index.get_words(l)) < count
                for l, count in slots_per_length.items()
            ):
                continue

            result = self._fill_grid(
                grid, slots, index, shuffled_by_length, size, seed
            )
            if result is not None:
                return result

        return None

    # -- Grid layout ----------------------------------------------------------

    def _generate_grid(
        self, size: int, rng: random.Random, density: float | None = None
    ) -> list[list[str]]:
        grid = [["." for _ in range(size)] for _ in range(size)]
        if density is None:
            density = rng.uniform(0.12, 0.20)
        black_target = int(size * size * density)
        placed = 0
        attempts = 0

        while placed < black_target and attempts < 500:
            attempts += 1
            r = rng.randint(0, size - 1)
            c = rng.randint(0, size - 1)
            if (r == size // 2 and c == size // 2) or grid[r][c] == "#":
                continue

            sr, sc = size - 1 - r, size - 1 - c
            grid[r][c] = "#"
            grid[sr][sc] = "#"
            delta = 2 if (r, c) != (sr, sc) else 1
            placed += delta

            if not self._validate_grid(grid, size):
                grid[r][c] = "."
                grid[sr][sc] = "."
                placed -= delta

        return grid

    def _validate_grid(self, grid: list[list[str]], size: int) -> bool:
        for r in range(size):
            run = 0
            for c in range(size):
                if grid[r][c] == "#":
                    if 1 <= run < self.MIN_WORD_LENGTH:
                        return False
                    run = 0
                else:
                    run += 1
            if 1 <= run < self.MIN_WORD_LENGTH:
                return False

        for c in range(size):
            run = 0
            for r in range(size):
                if grid[r][c] == "#":
                    if 1 <= run < self.MIN_WORD_LENGTH:
                        return False
                    run = 0
                else:
                    run += 1
            if 1 <= run < self.MIN_WORD_LENGTH:
                return False

        return True

    # -- Slot extraction ------------------------------------------------------

    def _extract_slots(self, grid: list[list[str]], size: int) -> list[Slot]:
        slots = []
        slot_id = 0

        for r in range(size):
            c = 0
            while c < size:
                if grid[r][c] != "#":
                    start = c
                    while c < size and grid[r][c] != "#":
                        c += 1
                    if c - start >= self.MIN_WORD_LENGTH:
                        slots.append(Slot(slot_id, r, start, "across", c - start))
                        slot_id += 1
                else:
                    c += 1

        for c in range(size):
            r = 0
            while r < size:
                if grid[r][c] != "#":
                    start = r
                    while r < size and grid[r][c] != "#":
                        r += 1
                    if r - start >= self.MIN_WORD_LENGTH:
                        slots.append(Slot(slot_id, start, c, "down", r - start))
                        slot_id += 1
                else:
                    r += 1

        return slots

    # -- Word loading ---------------------------------------------------------

    def _load_all_words(self, lang: str, difficulty: int) -> list[str]:
        key = (lang, difficulty)
        if key in self._word_cache:
            return list(self._word_cache[key])  # return copy to avoid mutation
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT word FROM words WHERE lang = ? AND difficulty_tier <= ? ORDER BY word",
                (lang, difficulty),
            )
            words = [row[0].upper() for row in cursor.fetchall()]
            self._word_cache[key] = words
            return list(words)
        finally:
            conn.close()

    # -- Filling with backtracking + index lookups ----------------------------

    def _fill_grid(
        self,
        grid: list[list[str]],
        slots: list[Slot],
        index: WordIndex,
        shuffled_by_length: dict[int, list[str]],
        size: int,
        seed: str,
    ) -> CrosswordResult | None:
        # Build crossing info
        cell_to_slot: dict[tuple[int, int], list[tuple[int, int]]] = {}
        for slot in slots:
            for i, cell in enumerate(slot.cells):
                cell_to_slot.setdefault(cell, []).append((slot.id, i))

        crossings: dict[int, list[tuple[int, int, int]]] = {s.id: [] for s in slots}
        for cell, entries in cell_to_slot.items():
            if len(entries) == 2:
                (id_a, pos_a), (id_b, pos_b) = entries
                crossings[id_a].append((id_b, pos_a, pos_b))
                crossings[id_b].append((id_a, pos_b, pos_a))

        slot_map = {s.id: s for s in slots}
        filled_grid = [row[:] for row in grid]
        assignment: dict[int, str] = {}
        used_words: set[str] = set()
        backtracks = 0

        def get_constraints(slot: Slot) -> dict[int, str]:
            constraints = {}
            for i, (r, c) in enumerate(slot.cells):
                v = filled_grid[r][c]
                if v not in (".", "#"):
                    constraints[i] = v
            return constraints

        def get_compat_set(slot: Slot) -> set[str]:
            """Get compatible word set from index, minus used words."""
            constraints = get_constraints(slot)
            compat = index.compatible(slot.length, constraints)
            if used_words:
                compat -= used_words
            return compat

        def get_candidates_ordered(compat: set[str], length: int) -> list[str]:
            """Return compatible words in shuffled order, capped."""
            result = []
            for w in shuffled_by_length[length]:
                if w in compat:
                    result.append(w)
                    if len(result) >= self.MAX_CANDIDATES_PER_STEP:
                        break
            return result

        def solve() -> bool:
            nonlocal backtracks
            if len(assignment) == len(slots):
                return True

            backtracks += 1
            if backtracks > self.MAX_BACKTRACKS:
                return False

            # Cheap MRV: pick slot with most constrained cells (letters already placed),
            # breaking ties by number of crossings. Only call compatible() for the winner.
            best_id = -1
            best_score = -1

            for s in slots:
                if s.id in assignment:
                    continue
                # Count how many cells already have letters (from crossing words)
                filled = sum(
                    1 for r, c in s.cells if filled_grid[r][c] not in (".", "#")
                )
                score = filled * 1000 + len(crossings[s.id])
                if score > best_score:
                    best_score = score
                    best_id = s.id

            if best_id == -1:
                return False

            slot = slot_map[best_id]
            compat = get_compat_set(slot)
            if not compat:
                return False
            candidates = get_candidates_ordered(compat, slot.length)

            for word in candidates:
                backtracks += 1
                if backtracks > self.MAX_BACKTRACKS:
                    return False

                # Place word
                old_cells = [filled_grid[r][c] for r, c in slot.cells]
                assignment[slot.id] = word
                used_words.add(word)
                for i, (r, c) in enumerate(slot.cells):
                    filled_grid[r][c] = word[i]

                # Forward check: crossing slots must still have candidates
                ok = True
                for cross_id, _, _ in crossings[slot.id]:
                    if cross_id in assignment:
                        continue
                    cross_slot = slot_map[cross_id]
                    cross_constraints = get_constraints(cross_slot)
                    if not index.has_any_compatible(
                        cross_slot.length, cross_constraints, used_words
                    ):
                        ok = False
                        break

                if ok and solve():
                    return True

                # Undo
                del assignment[slot.id]
                used_words.discard(word)
                for (r, c), val in zip(slot.cells, old_cells):
                    filled_grid[r][c] = val

            return False

        if not solve():
            return None

        black_cells = [
            (r, c) for r in range(size) for c in range(size) if grid[r][c] == "#"
        ]
        placed_words = [PlacedWord(word=assignment[s.id], slot=s) for s in slots]
        self._assign_clue_numbers(placed_words)

        return CrosswordResult(
            size=size,
            grid=filled_grid,
            black_cells=black_cells,
            placed_words=placed_words,
            seed=seed,
        )

    @staticmethod
    def _assign_clue_numbers(placed_words: list[PlacedWord]):
        starts: dict[tuple[int, int], list[PlacedWord]] = {}
        for pw in placed_words:
            key = (pw.slot.row, pw.slot.col)
            starts.setdefault(key, []).append(pw)

        for number, key in enumerate(sorted(starts.keys()), start=1):
            for pw in starts[key]:
                pw.clue_number = number
