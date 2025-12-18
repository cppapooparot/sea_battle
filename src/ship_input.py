from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Tuple

from src.utils import Coord, neighbors_8, parse_xy, new_ship_board, render_board

SHIP_SIZES: List[int] = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

@dataclass(frozen=True)
class Ship:
    ship_id: int
    cells: Tuple[Coord, ...]

    @property
    def size(self) -> int:
        return len(self.cells)

    
def cells_from_segment(a: Coord, b: Coord) -> List[Coord]:
    """
    Expand a-b into list of cells like a, ..., b
    a and b must be in the same row or column
    """
    ax, ay = a
    bx, by = b

    if ax == bx: # vertical ship
        y1, y2 = sorted((ay, by))
        return [(ax, y) for y in range(y1, y2 + 1)]
    if ay == by: # horizontal
        x1, x2 = sorted((ax, bx))
        return [(x, ay) for x in range(x1, x2 + 1)]
    
    raise ValueError("Ship must be only vertical or horizontal")

def parse_ship_location(line: str, expected_size: int) -> List[Coord]:
    """
    Format:
        size 1: "xy" or "xy-xy"
        size > 1: "xy-xy"
    """
    s = line.strip()
    if not s:
        raise ValueError("Empty ship input")
    
    if "-" in s:
        left, right = [p.strip() for p in s.split("-", 1)]
        a = parse_xy(left)
        b = parse_xy(right)
        cells = cells_from_segment(a, b)
    else:
        if expected_size != 1:
            raise ValueError("If ship size > 1 use format 'xy-xy'")
        cells = [parse_xy(s)]
    if len(cells) != expected_size:
        raise ValueError(f"Ship length mismatch: expected {expected_size}, got {len(cells)}.")
    if len(set(cells)) != len(cells):
        raise ValueError("Ship contains duplicate cells.")
    return cells


def validate_no_touch(ships: List[Ship]) -> None:
    # Validate that ships do not overlap and touch each other
    occupied: Set[Coord] = set()

    for ship in ships:
        # overlap check
        for c in ship.cells:
            if c in occupied:
                raise ValueError(f"Overlapping ship cell at {c}")

        # check if ships touch each other
        for c in ship.cells:
            for n in neighbors_8(c):
                if n in occupied:
                    raise ValueError(f"Ships touch near {c} and {n}")

        # add ship after checks
        for c in ship.cells:
            occupied.add(c)

def input_player_ships() -> List[Ship]:
    print("Enter ships in format 'xy-xy'")
    print("For size 1 you can enter just 'xy'.")
    print("Ship sizes:", SHIP_SIZES)

    ships: List[Ship] = []
    board = new_ship_board()

    for idx, size in enumerate(SHIP_SIZES, start=1):
        while True:
            try:
                line = input(f"Ship #{idx} (size {size}) > ")
                cells = parse_ship_location(line, expected_size=size)
                ships.append(Ship(ship_id=idx, cells=tuple(cells)))

                validate_no_touch(ships)

                # draw ship on the board (after validation)
                for (x, y) in cells:
                    board[y][x] = "S"

                print(render_board(board, title="Your ships"))
                break
            except ValueError as e:
                if len(ships) == idx:  # rollback last append
                    ships.pop()
                print(f"Invalid ship: {e}")
    return ships

def save_ships_csv(ships: List[Ship], path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ship_id", "size", "x", "y"])
        for ship in ships:
            for (x, y) in ship.cells:
                w.writerow([ship.ship_id, ship.size, x, y])
            
def run_ship_input(path: str = "data/player_ships.csv") -> List[Ship]:
    ships = input_player_ships()
    save_ships_csv(ships, path)
    print(f"Saved player ships to {path}")
    return ships

def load_ships_csv(path: str) -> List[Ship]:
    ships_by_id: dict[int, List[Coord]] = {}

    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ship_id = int(row["ship_id"])
            x = int(row["x"])
            y = int(row["y"])
            ships_by_id.setdefault(ship_id, []).append((x, y))
        
    ships: List[Ship] = []
    for ship_id, cells in sorted(ships_by_id.items()):
        ships.append(Ship(ship_id=ship_id, cells=tuple(cells)))

    validate_no_touch(ships)
    return ships
