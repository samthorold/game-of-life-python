from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


OPPOSITE_DIRECTION = [
    ("n", "s"),
    ("ne", "sw"),
    ("e", "w"),
    ("se", "nw"),
    ("s", "n"),
    ("sw", "ne"),
    ("w", "e"),
    ("nw", "se"),
]


@dataclass
class Cell:
    n: Cell | None = None
    ne: Cell | None = None
    e: Cell | None = None
    se: Cell | None = None
    s: Cell | None = None
    sw: Cell | None = None
    w: Cell | None = None
    nw: Cell | None = None
    alive: bool = False
    nfriends: int = 0

    def update_status(self, value: bool) -> None:
        for neighbour_addr in "n ne e se s sw w nw".split():
            neighbour: Cell = getattr(self, neighbour_addr)
            if neighbour:
                neighbour.nfriends += 1 if value else -1
        self.alive = value

    def set_neighbour(self, direction: str, cell: Cell) -> None:
        setattr(self, direction, cell)
        self.nfriends += 1 if cell.alive else 0

    @property
    def alive_next_generation(self) -> bool:
        return self.nfriends in [2, 3] if self.alive else self.nfriends == 3

    def tell_neighbours_removed(self):
        for addr, friend in OPPOSITE_DIRECTION:
            if getattr(self, addr) is not None:
                # No Cell.set because don't remove alive cells
                setattr(getattr(self, addr), friend, None)


class Board:
    def __init__(self, state: Sequence[tuple[int, int]]):
        self.height = max([y for y, _ in state]) + 1
        self.width = max([x for _, x in state]) + 1

        self.cells: list[list[Cell]] = []
        self.previous_states: list[int] = []

        rows: list[list[int]] = [[] for _ in range(self.height)]

        for row_idx, col_idx in state:
            rows[row_idx].append(col_idx)

        for row in rows:
            self.append_row(row)

        self.prepend_col()
        self.prepend_row()
        self.append_col()
        self.append_row()

        while len(self.cells[0]) < self.width:
            self.append_col()

        while len(self.cells) < self.height:
            self.append_row()

    def __hash__(self):
        return hash(tuple(tuple(cell.alive for cell in row) for row in self.cells))

    @property
    def repeated_previous_states(self):
        return self.previous_states[-1] in self.previous_states[:-1]

    def append_row(self, state: Sequence[int] | None = None) -> list[Cell]:
        state = [] if state is None else state
        row = len(self.cells)
        self.cells.append([])
        for col in range(self.width):
            c = Cell()
            self.cells[-1].append(c)
            if col in state:
                c.alive = True
            # N/S
            if row > 0:
                c.set_neighbour("n", self.cells[row - 1][col])
                self.cells[row - 1][col].set_neighbour("s", c)
                # NW/SE
                if col > 0:
                    c.set_neighbour("nw", self.cells[row - 1][col - 1])
                    self.cells[row - 1][col - 1].set_neighbour("se", c)
                # NE/SW
                if col < (self.width - 1):
                    c.set_neighbour("ne", self.cells[row - 1][col + 1])
                    self.cells[row - 1][col + 1].set_neighbour("sw", c)

            # E/W
            if col > 0:
                c.set_neighbour("w", self.cells[row][col - 1])
                self.cells[row][col - 1].set_neighbour("e", c)

        self.height = max(self.height, len(self.cells))

        return self.cells[-1]

    def append_col(self, state: Sequence[int] | None = None) -> list[Cell]:
        state = [] if state is None else state

        for row in range(self.height):
            c = Cell()
            self.cells[row].append(c)
            if row in state:
                c.alive = True
            # N/S
            if row > 0:
                # N/S
                c.set_neighbour("n", self.cells[row - 1][-1])
                self.cells[row - 1][-1].set_neighbour("s", c)
                # NW/SE
                c.set_neighbour("nw", self.cells[row - 1][-2])
                self.cells[row - 1][-2].set_neighbour("se", c)
                # NE/SW - for the like previously appended col
                self.cells[row][-2].set_neighbour("ne", self.cells[row - 1][-1])
                self.cells[row - 1][-1].set_neighbour("sw", self.cells[row][-2])

            # E/W
            c.set_neighbour("w", self.cells[row][-2])
            self.cells[row][-2].set_neighbour("e", c)

        self.width = max(self.width, len(self.cells[0]))

        return [r[-1] for r in self.cells]

    def prepend_row(self, state: Sequence[int] | None = None) -> list[Cell]:
        state = [] if state is None else state
        self.cells.insert(0, [])
        for col in range(self.width):
            c = Cell()
            self.cells[0].append(c)
            if col in state:
                c.alive = True
            # N/S
            c.set_neighbour("s", self.cells[1][col])
            self.cells[1][col].set_neighbour("n", c)
            # NW/SE
            if col < self.width - 1:
                c.set_neighbour("se", self.cells[1][col + 1])
                self.cells[1][col + 1].set_neighbour("nw", c)
            # NE/SW
            if col > 0:
                c.set_neighbour("sw", self.cells[1][col - 1])
                self.cells[1][col - 1].set_neighbour("ne", c)

                c.set_neighbour("w", self.cells[0][col - 1])
                self.cells[0][col - 1].set_neighbour("e", c)

        self.height = max(self.height, len(self.cells))

        return self.cells[0]

    def prepend_col(self, state: Sequence[int] | None = None) -> list[Cell]:
        state = [] if state is None else state

        for row in range(self.height):
            c = Cell()
            self.cells[row].insert(0, c)
            if row in state:
                c.alive = True
            # N/S
            if row > 0:
                c.set_neighbour("n", self.cells[row - 1][0])
                self.cells[row - 1][0].set_neighbour("s", c)
                # NE/SW
                c.set_neighbour("ne", self.cells[row - 1][1])
                self.cells[row - 1][1].set_neighbour("sw", c)
                # NW/SE
                self.cells[row][1].set_neighbour("nw", self.cells[row - 1][0])
                self.cells[row - 1][0].set_neighbour("se", self.cells[row][1])

            # E/W
            c.set_neighbour("e", self.cells[row][1])
            self.cells[row][1].set_neighbour("w", c)

        self.width = max(self.width, len(self.cells[0]))

        return [r[0] for r in self.cells]

    def __str__(self) -> str:
        s = ""
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                if cell.alive:
                    s += "x"
                else:
                    s += "."
            s += "\n"
        return s

    @property
    def all_dead(self):
        return not any(c.alive for row in self.cells for c in row)

    @property
    def state(self) -> tuple[list[tuple[int, int]], tuple[int, int]]:
        state: list[tuple[int, int]] = []
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                if cell.alive:
                    state.append((y, x))
        return state, (self.height, self.width)

    def next_generation(self, fit_board: bool = True) -> bool:
        self.previous_states.append(hash(self))

        # if fit_board:
        #     self.fit_board_to_cells()
        max_row = len(self.cells) - 1
        max_col = len(self.cells[0]) - 1
        prepend_row = append_row = prepend_col = append_col = False
        alive: list[list[bool]] = []
        for y, row in enumerate(self.cells):
            alive.append([])
            for cell in row:
                alive[y].append(cell.alive_next_generation)
        changed = False
        for row_idx, (row_status, row) in enumerate(zip(alive, self.cells)):
            for col_idx, (cell_status, cell) in enumerate(zip(row_status, row)):
                if cell.alive != cell_status:
                    changed = True
                    cell.update_status(cell_status)
                    # if making a cell on the perimeter alive
                    # need buffer of dead cells around it
                    if cell_status:
                        if row_idx == 0:
                            prepend_row = True
                        if row_idx == max_row:
                            append_row = True
                        if col_idx == 0:
                            prepend_col = True
                        if col_idx == max_col:
                            append_col = True

        if prepend_row:
            self.prepend_row()
        if append_row:
            self.append_row()
        if prepend_col:
            self.prepend_col()
        if append_col:
            self.append_col()

        return changed
