import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.solver.dlx import DLX


def test_simple_exact_cover():
    """Knuth's classic example: rows that exactly cover columns {1..7}."""
    dlx = DLX()
    for i in range(1, 8):
        dlx.add_column(str(i))

    dlx.add_row("A", ["1", "4", "7"])
    dlx.add_row("B", ["1", "4"])
    dlx.add_row("C", ["4", "5", "7"])
    dlx.add_row("D", ["3", "5", "6"])
    dlx.add_row("E", ["2", "3", "6", "7"])
    dlx.add_row("F", ["2", "7"])

    solutions = dlx.solve(max_solutions=100)
    assert len(solutions) == 1, f"Expected 1 solution, got {len(solutions)}"
    assert set(solutions[0]) == {"B", "D", "F"}, f"Wrong solution: {solutions[0]}"
    print("test_simple_exact_cover PASSED")


def test_no_solution():
    """Problem with no valid exact cover."""
    dlx = DLX()
    for c in ["c1", "c2", "c3"]:
        dlx.add_column(c)

    dlx.add_row("r1", ["c1", "c2"])
    dlx.add_row("r2", ["c1", "c3"])
    # No row covers c2+c3 without c1, so no exact cover exists

    solutions = dlx.solve(max_solutions=100)
    assert len(solutions) == 0, f"Expected 0 solutions, got {len(solutions)}"
    print("test_no_solution PASSED")


def test_multiple_solutions():
    """Problem with exactly two solutions."""
    dlx = DLX()
    for c in ["c1", "c2"]:
        dlx.add_column(c)

    dlx.add_row("r1", ["c1", "c2"])
    dlx.add_row("r2", ["c1"])
    dlx.add_row("r3", ["c2"])

    solutions = dlx.solve(max_solutions=100)
    solution_sets = [set(s) for s in solutions]
    assert len(solutions) == 2, f"Expected 2 solutions, got {len(solutions)}"
    assert {"r1"} in solution_sets
    assert {"r2", "r3"} in solution_sets
    print("test_multiple_solutions PASSED")


def test_single_column():
    """Trivial case: one column, two competing rows."""
    dlx = DLX()
    dlx.add_column("x")
    dlx.add_row("a", ["x"])
    dlx.add_row("b", ["x"])

    solutions = dlx.solve(max_solutions=100)
    assert len(solutions) == 2, f"Expected 2 solutions, got {len(solutions)}"
    print("test_single_column PASSED")


def test_max_solutions_limit():
    """Verify that max_solutions caps the returned results."""
    dlx = DLX()
    dlx.add_column("x")
    dlx.add_row("a", ["x"])
    dlx.add_row("b", ["x"])

    solutions = dlx.solve(max_solutions=1)
    assert len(solutions) == 1, f"Expected 1 solution, got {len(solutions)}"
    print("test_max_solutions_limit PASSED")


def test_identity_matrix():
    """Identity matrix: each row covers exactly one unique column."""
    dlx = DLX()
    n = 5
    for i in range(n):
        dlx.add_column(f"c{i}")
    for i in range(n):
        dlx.add_row(f"r{i}", [f"c{i}"])

    solutions = dlx.solve(max_solutions=100)
    assert len(solutions) == 1, f"Expected 1 solution, got {len(solutions)}"
    assert set(solutions[0]) == {f"r{i}" for i in range(n)}
    print("test_identity_matrix PASSED")


if __name__ == "__main__":
    test_simple_exact_cover()
    test_no_solution()
    test_multiple_solutions()
    test_single_column()
    test_max_solutions_limit()
    test_identity_matrix()
    print("\nAll tests passed!")
