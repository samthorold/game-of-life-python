def is_rle_cells_line(line: str) -> bool:
    if line.startswith("#N"):
        return False
    if any(line.startswith(s) for s in ["#C", "#O"]):
        return False
    if "," in line:
        return False
    return True


def parse_rle_line(string: str) -> tuple[tuple[int, int, bool], ...]:
    x = y = width = 0
    ns = ""
    cells = []
    for ch in string:
        if ch == "!":
            while x < width:
                cells.append((x, y, False))
                x += 1
        if ch == "$":
            y += int(ns or 1)
            x = 0
            ns = ""
        if ch in "123456789":
            ns += ch
        if ch in "bo":
            alive = True if ch == "o" else False
            for _ in range(int(ns or 1)):
                cells.append((x, y, alive))
                x += 1
                width = max(x, width)
            ns = ""
    return tuple(cells)


def rle(string: str) -> tuple[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    for line in string.split("\n"):
        if is_rle_cells_line(line := line.strip()):
            for x, y, alive in parse_rle_line(line):
                if alive:
                    cells.append((y, x))
    return tuple(cells)
