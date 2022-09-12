from pprint import pprint

from handlers import handle


def rle(string: str) -> tuple[tuple[int, int]]:
    res = [handle(line) for line in string.split("\n")]
    cell_res = next(r for r in res if hasattr(r, "cells"))
    return cell_res
