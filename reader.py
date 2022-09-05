from pprint import pprint

from handlers import handle


def rle(string: str) -> str:
    res = [handle(line) for line in string.split("\n")]
    pprint(res)
    return ""
