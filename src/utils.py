from __future__ import annotations

from typing import List, Optional, Tuple

BOARD_SIZE = 10  # the map size is (10, 10)

Coord = Tuple[int, int]  # (x, y) 0-9

def parse_xy(s: str) -> Coord:
    """
    Parse coordinates in formats: 'xy', 'x y', 'x,y', 'x, y' where x,y are 0..9.
    Returns (x, y).
    """
    s = s.strip()
    if not s:
        raise ValueError("Empty coordinates")

    if len(s) == 2 and s.isdigit():
        x, y = int(s[0]), int(s[1])
    else:
        parts = [p for p in s.replace(",", " ").split() if p]
        if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
            raise ValueError("Bad coordinate format, use 'xy', 'x,y' or 'x y'")
        x, y = int(parts[0]), int(parts[1])

    if not in_bounds(x, y):
        raise ValueError(f"Out of bounds: {(x, y)}. Must be 0..9 for both.")

    return (x, y)
    
def in_bounds(x: int, y: int, size: int = BOARD_SIZE) -> bool: # check if cords are valid 
    return 0 <= x < size and 0 <= y < size

def neighbors_4(c: Coord) -> List[Coord]:
    # up, down, left, right neighbors if in bounds
    x, y = c
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    return [(cx, cy) for  (cx, cy) in neighbors if in_bounds(cx, cy)]

def neighbors_8(c: Coord) -> List[Coord]:
    # All 8 neighbors if in bounds 
    x, y = c
    out: List[Coord] = []
    for X in (-1, 0, 1):
        for Y in (-1, 0, 1):
            if X == 0 and Y == 0:
                continue
            cx, cy = x + X, y + Y #getting all neigbors including outside
            if in_bounds(cx, cy):
                out.append((cx, cy))
    return out



