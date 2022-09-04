"""
http://pi.math.cornell.edu/~lipa/mec/lesson6.html

Game has "generations" - like a "turn".

The game "board" is an infinite 2D grid.

Each cell has 8 "neighbours", including diagonal.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

parser = argparse.ArgumentParser()
parser.add_argument("size", type=int, help="Board size")
parser.add_argument("initial_state", help="E.g. '1,1;3,2'")


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
    def __init__(self, initial_state: list[tuple[int, int]], size: int = 16):
        self.size = size

        cells: list[list[Cell]] = []
        for row in range(size):
            cells.append([])
            for col in range(size):
                c = Cell()
                cells[row].append(c)
                if (row, col) in initial_state:
                    c.alive = True
                # N/S
                if row > 0:
                    c.n = cells[row - 1][col]
                    cells[row - 1][col].s = c
                    # NW/SE
                    if col > 0:
                        c.nw = cells[row - 1][col - 1]
                        cells[row - 1][col - 1].se = c
                    # NE / SW
                    if col < (size - 1):
                        c.ne = cells[row - 1][col + 1]
                        cells[row - 1][col + 1].sw = c
                # E/W
                if col > 0:
                    c.w = cells[row][col - 1]
                    cells[row][col - 1].e = c
        self.cells = cells

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

    def next_generation(self):
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
        for row_status, row in zip(alive, self.cells):
            for cell_status, cell in zip(row_status, row):
                cell.alive = cell_status


if __name__ == "__main__":
    print("Game of Life")

    args = parser.parse_args()
    size = args.size
    initial_state = [
        tuple([int(x) for x in s.split(",")])
        for s in args.initial_state.split(";")
    ]
    b = Board(initial_state, size)
    print(b)
    for i in range(10):
        b.next_generation()
        print(b)
