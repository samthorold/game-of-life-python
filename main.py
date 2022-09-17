"""
http://pi.math.cornell.edu/~lipa/mec/lesson6.html
"""

from __future__ import annotations

import argparse
import time

import models
import reader


parser = argparse.ArgumentParser()
parser.add_argument("--string")
parser.add_argument("--path", default="gol_patterns/1beacon.rle")
parser.add_argument("--type", default="rle")
parser.add_argument("--offset", default="0,0", help="Offset: (from top, from left)")
parser.add_argument("-N", "--iterations", type=int, default=15)
parser.add_argument("--delay", type=float, default=0.2)


if __name__ == "__main__":
    print("Game of Life")

    args = parser.parse_args()

    if args.string is None:
        with open(args.path) as f:
            string = f.read()
    else:
        string = args.string
    print(string)
    alive_cells = getattr(reader, args.type)(string)
    b = models.Board(alive_cells)
    print(b)
    for i in range(args.iterations):
        if args.delay:
            time.sleep(args.delay)
        changed = b.next_generation()
        print(i + 1)
        print(b)
        if not changed or b.all_dead:
            break
