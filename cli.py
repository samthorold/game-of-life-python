import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--string")
parser.add_argument("--path", default="gol_patterns/1beacon.rle")
parser.add_argument("--type", default="rle")
parser.add_argument("--offset", default="0,0", help="Offset: (from top, from left)")
parser.add_argument("-N", "--iterations", type=int, default=15)
parser.add_argument("--delay", type=float, default=0.2)
