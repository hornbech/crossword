import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.solver.dlx import DLX


def test_dlx():
    dlx = DLX()
    # Setup columns
    col1 = dlx.add_column("c1")
    col2 = dlx_temp_placeholder_ref = dlx.add_column("c2")
    col3 = dlx.add_column("c3")

    # Add rows (Exact cover problem)
    dlx.add_row("r1", ["c1", "c2"])
    dlx.add_row("r2", ["c2", "c3"])
    dlx.add_row("r3", ["c1", "c3"])

    solutions = dlx.solve()
    print(f"Found {len(solutions)} solutions")
    for sol in solutions:
        print(f"Solution: {sol}")

    if len(solutions) > 0:
        print("Test Passed!")
    else:
        print("Test Failed: No solutions found for a valid problem.")


if __name__ == "__main__":
    test_dlx()
