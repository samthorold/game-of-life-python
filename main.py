"""
http://pi.math.cornell.edu/~lipa/mec/lesson6.html
"""

import time

import cli
import models
import reader


if __name__ == "__main__":
    print("Game of Life")

    args = cli.parser.parse_args()

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
