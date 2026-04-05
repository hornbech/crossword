class DLXNode:
    __slots__ = ("row_id", "col", "left", "right", "up", "down")

    def __init__(self, row_id=None, col=None):
        self.row_id = row_id
        self.col = col
        self.left = self
        self.right = self
        self.up = self
        self.down = self


class DLXColumn(DLXNode):
    __slots__ = ("name", "size")

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.size = 0
        self.col = self


class DLX:
    def __init__(self):
        self.root = DLXColumn("root")
        self.columns_map: dict[str, DLXColumn] = {}

    def add_column(self, name: str) -> DLXColumn:
        if name in self.columns_map:
            return self.columns_map[name]
        col = DLXColumn(name)
        # Insert at left end of header row (before root)
        col.right = self.root
        col.left = self.root.left
        self.root.left.right = col
        self.root.left = col
        self.columns_map[name] = col
        return col

    def add_row(self, row_id, col_names: list[str]):
        if not col_names:
            return
        first_node = None
        for name in col_names:
            col = self.columns_map.get(name)
            if col is None:
                continue
            node = DLXNode(row_id=row_id, col=col)
            # Link into column (insert above column header)
            node.down = col
            node.up = col.up
            col.up.down = node
            col.up = node
            col.size += 1
            # Link into row
            if first_node is None:
                first_node = node
            else:
                node.left = first_node.left
                node.right = first_node
                first_node.left.right = node
                first_node.left = node

    @staticmethod
    def _cover(col: DLXColumn):
        col.right.left = col.left
        col.left.right = col.right
        row = col.down
        while row is not col:
            node = row.right
            while node is not row:
                node.down.up = node.up
                node.up.down = node.down
                node.col.size -= 1
                node = node.right
            row = row.down

    @staticmethod
    def _uncover(col: DLXColumn):
        row = col.up
        while row is not col:
            node = row.left
            while node is not row:
                node.col.size += 1
                node.down.up = node
                node.up.down = node
                node = node.left
            row = row.up
        col.right.left = col
        col.left.right = col

    def solve(self, max_solutions: int = 1) -> list[list]:
        solutions: list[list] = []
        self._search([], solutions, max_solutions)
        return solutions

    def _search(self, partial: list, solutions: list[list], max_solutions: int):
        if self.root.right is self.root:
            solutions.append(list(partial))
            return

        if len(solutions) >= max_solutions:
            return

        # Choose column with fewest nodes (MRV heuristic)
        best = None
        min_size = float("inf")
        col = self.root.right
        while col is not self.root:
            if col.size < min_size:
                min_size = col.size
                best = col
            col = col.right

        if best is None or best.size == 0:
            return

        self._cover(best)

        row = best.down
        while row is not best:
            partial.append(row.row_id)

            # Cover all other columns in this row
            node = row.right
            while node is not row:
                self._cover(node.col)
                node = node.right

            self._search(partial, solutions, max_solutions)

            # Uncover in reverse order
            node = row.left
            while node is not row:
                self._uncover(node.col)
                node = node.left

            partial.pop()

            if len(solutions) >= max_solutions:
                break

            row = row.down

        self._uncover(best)
