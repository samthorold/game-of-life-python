"""
http://pi.math.cornell.edu/~lipa/mec/lesson6.html
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import time
from typing import Sequence

import reader


parser = argparse.ArgumentParser()
parser.add_argument("--string")
parser.add_argument("--path", default="gol_patterns/1beacon.rle")
parser.add_argument("--type", default="rle")
parser.add_argument("--size", type=int, default=16, help="Board size")
parser.add_argument("--offset", default="0,0", help="Offset: (from top, from left)")
parser.add_argument("-N", "--iterations", type=int, default=15)
parser.add_argument("--delay", type=float, default=0)


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

    def alive_neighbours(self):
        neighbours: list[Cell] = []
        for neighbour_addr in "n ne e se s sw w nw".split():
            neighbour = getattr(self, neighbour_addr)
            if neighbour and neighbour.alive:
                neighbours.append(neighbour)
        return neighbours


class Board:
    @staticmethod
    def from_string(
        string: str, size: int, delim=None, alive: str = "x", offset=(0, 0)
    ) -> Board:
        yoff, xoff = offset
        state: list[tuple[int, int]] = []
        rows = string.split(delim)
        for y, row in enumerate(rows):
            for x, alv in enumerate(row):
                if alv == alive:
                    state.append((y + yoff, x + xoff))
        return Board(state=state, height=size, width=size)

    def __init__(
        self, state: Sequence[tuple[int, int]], height: int = 16, width: int = 16
    ):
        self.height = height
        self.width = width
        self.cells: list[list[Cell]] = []

        rows = []

        for row_idx, col_idx in state:
            while len(rows) - 1 < row_idx:
                rows.append([])
            rows[row_idx].append(col_idx)

        for row in rows:
            self.append_row(row)

        while len(self.cells[0]) < self.width:
            self.append_col()

        while len(self.cells) < self.height:
            self.append_row()

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
                c.n = self.cells[row - 1][col]
                self.cells[row - 1][col].s = c
                # NW/SE
                if col > 0:
                    c.nw = self.cells[row - 1][col - 1]
                    self.cells[row - 1][col - 1].se = c
                # NE/SW
                if col < (self.width - 1):
                    c.ne = self.cells[row - 1][col + 1]
                    self.cells[row - 1][col + 1].sw = c
            # E/W
            if col > 0:
                c.w = self.cells[row][col - 1]
                self.cells[row][col - 1].e = c

        self.height = max(self.height, len(self.cells))

        return self.cells[-1]

    def append_col(self, state: Sequence[int] | None = None) -> list[Cell]:
        state = [] if state is None else state
        col = len(self.cells[0])

        for row in range(self.height):
            c = Cell()
            self.cells[row].append(c)
            if row in state:
                c.alive = True
            # N/S
            if row > 0:
                c.n = self.cells[row - 1][col]
                self.cells[row - 1][col].s = c
                # NW/SE
                c.nw = self.cells[row - 1][col - 1]
                self.cells[row - 1][col - 1].se = c

            # E/W
            c.w = self.cells[row][col - 1]
            self.cells[row][col - 1].e = c

        self.width = max(self.width, len(self.cells[0]))

        return [r[-1] for r in self.cells]

    def prepend_row(self, state: Sequence[int] | None = None) -> list[Cell]:
        state = [] if state is None else state
        self.cells = [[]] + self.cells
        for col in range(self.width):
            c = Cell()
            self.cells[0].append(c)
            if col in state:
                c.alive = True
            # N/S
            c.s = self.cells[1][col]
            self.cells[1][col].n = c
            # NW/SE
            if col > 0:
                c.se = self.cells[1][col - 1]
                self.cells[1][col - 1].nw = c
            # NE / SW
            if col < (self.width - 1):
                c.sw = self.cells[1][col + 1]
                self.cells[1][col + 1].ne = c
            # E/W
            if col > 0:
                c.w = self.cells[0][col - 1]
                self.cells[0][col - 1].e = c

        self.height = max(self.height, len(self.cells))

        return self.cells[0]

    def prepend_col(self, state: Sequence[int] | None = None) -> list[Cell]:
        state = [] if state is None else state

        for row in range(self.height):
            # print(f"prepend_col {row=}")
            c = Cell()
            self.cells[row] = [c] + self.cells[row]
            if row in state:
                c.alive = True
            # N/S
            if row > 0:
                c.n = self.cells[row - 1][1]
                self.cells[row - 1][1].s = c
                # NE/SW
                c.ne = self.cells[row - 1][1]
                self.cells[row - 1][1].sw = c

            c.e = self.cells[row][1]
            self.cells[row][1].w = c

        self.width = max(self.width, len(self.cells[0]))

        return [r[-1] for r in self.cells]

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
        if fit_board:
            self.fit_board_to_cells()
        alive: list[list[bool]] = []
        for y, row in enumerate(self.cells):
            alive.append([])
            for cell in row:
                if cell.alive:
                    if len(cell.alive_neighbours()) in [2, 3]:
                        alive[y].append(True)
                    else:
                        alive[y].append(False)
                else:
                    if len(cell.alive_neighbours()) == 3:
                        alive[y].append(True)
                    else:
                        alive[y].append(False)
        changed = False
        for row_status, row in zip(alive, self.cells):
            for cell_status, cell in zip(row_status, row):
                if cell.alive != cell_status:
                    changed = True
                cell.alive = cell_status

        if fit_board:
            self.fit_board_to_cells()

        return changed

    def check_perimeter_alive(self) -> tuple[bool, bool, bool, bool]:
        left = right = False
        for row in self.cells:
            if row[0].alive:
                left = True
            if row[-1].alive:
                right = True
        top = any(c.alive for c in self.cells[0])
        bottom = any(c.alive for c in self.cells[-1])
        return left, top, right, bottom

    def fit_board_to_cells(self) -> bool:
        ltrb = self.check_perimeter_alive()
        if not any(ltrb):
            return False
        l, t, r, b = ltrb

        if l:
            self.prepend_col()
        if t:
            self.prepend_row()
        if r:
            self.append_col()
        if b:
            self.append_row()

        return True


if __name__ == "__main__":
    print("Game of Life")

    args = parser.parse_args()
    size = args.size

    if args.string is None:
        with open(args.path) as f:
            string = f.read()
        cell_res = getattr(reader, args.type)(string)
        b = Board(cell_res.to_xy(), size, size)
    else:
        initial_state = tuple(
            [
                tuple([int(x) for x in s.split(",")])
                for s in args.initial_state.split(";")
            ]
        )
        b = Board(initial_state, size, size)
    print(b)
    for i in range(args.iterations):
        if args.delay:
            time.sleep(args.delay)
        changed = b.next_generation()
        print(b)
        if not changed or b.all_dead:
            break
