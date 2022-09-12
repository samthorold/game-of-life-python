from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeVar, Callable


T = TypeVar("T")


class LineType(Enum):
    CELLS = auto()
    COMMENT = auto()
    HEADER = auto()
    NAME = auto()


@dataclass
class HeaderResult:
    x: int
    y: int
    rule: str | None = None


@dataclass
class NameResult:
    name: str


@dataclass
class CommentResult:
    comment: str


@dataclass
class Cell:
    x: int
    y: int
    alive: bool


@dataclass
class CellsResult:
    cells: tuple[Cell]

    def to_xy(self) -> tuple[tuple[int, int]]:
        return tuple([(c.y, c.x) for c in self.cells])


def identify_line(line: str) -> LineType:
    if line.startswith("#N"):
        return LineType.NAME
    if line.startswith("#C"):
        return LineType.COMMENT
    if "," in line:
        return LineType.HEADER
    return LineType.CELLS


class HeaderParseError(Exception):
    """Error when parsing header row part string, e.g. 'x = 3, y=3'."""


def header_part_value(t: Callable[[str], T], part: str) -> T:
    if "=" not in part:
        raise HeaderParseError(f"Could not convert {part}. No '=' in header part.")
    val = part.split("=")[-1].strip()
    try:
        return t(val)
    except:
        raise HeaderParseError(f"Could not convert {val} to {T}.")


def parse_header(string: str) -> tuple[int, int, str | None]:
    """Parse the pattern header string."""
    parts = string.split(",")
    x = y = rule = None
    for part in parts:
        if "x" in part:
            x = header_part_value(int, part)
        if "y" in part:
            y = header_part_value(int, part)
        if "rule" in part:
            rule = header_part_value(str, part)
    if x is None or y is None:
        raise HeaderParseError(f"Size missing from header '{string}'")
    return x, y, rule


def parse_name(string: str) -> str:
    return string[2:].strip()


def parse_comment(string: str) -> str:
    return string[2:].strip()


def parse_cells(string: str) -> tuple[tuple[int, int, bool], ...]:
    x = y = 0
    ns = ""
    cells = []
    for ch in string:
        if ch == "$":
            y += 1
            x = 0
            continue
        if ch in "123456789":
            ns += ch
        if ch in "bo":
            alive = True if ch == "o" else False
            for _ in range(int(ns or 1)):
                cells.append((x, y, alive))
                x += 1
            ns = ""
    return tuple(cells)


def header(line: str) -> HeaderResult:
    return HeaderResult(*parse_header(line))


def name(line: str) -> NameResult:
    return NameResult(parse_name(line))


def cells(line: str) -> CellsResult:
    return CellsResult(tuple(Cell(*c) for c in parse_cells(line)))


def comment(line: str) -> CommentResult:
    return CommentResult(parse_comment(line))


HANDLERS = {
    LineType.HEADER: header,
    LineType.NAME: name,
    LineType.COMMENT: comment,
    LineType.CELLS: cells,
}


def handle(line: str):
    return HANDLERS[identify_line(line)](line)
