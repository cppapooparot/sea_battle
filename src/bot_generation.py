from __future__ import annotations
import random
from typing import List, Set

from src.ship_input import Ship, SHIP_SIZES, validate_no_touch, save_ships_csv
from src.utils import Coord, neighbors_8

Orientation = str # 'h' for horizontal and 'v' vertical


def generate_ship_cells_from_start(start: Coord, size: int, orientation: Orientation) -> List[Coord]:
    x, y = start
    if orientation == "h":
        return [(x + i, y) for i in range(size)]
    return [(x, y + i) for i in range(size)]

def cells_in_bounds(cells: List[Coord], board_size: int = 10) -> bool:
    return all(0 <= x < board_size and 0 <= y < board_size for x, y in cells)

def touches_occupied(cells: List[Coord], occupied: Set[Coord]) -> bool:
    for c in cells:
        if c in occupied:
            return True
        for n in neighbors_8(c):
            if n in occupied:
                return True
    return False

def generate_bot_ships(seed: int | None = None) -> List[Ship]:
    rng = random.Random(seed)

    ships: List[Ship] = []
    occupied: Set[Coord] = set()

    for ship_id, size in enumerate(SHIP_SIZES, start=1):
        while True:
            orientation: Orientation = rng.choice(["h", "v"])
            start = (rng.randrange(10), rng.randrange(10))
            cells = generate_ship_cells_from_start(start, size, orientation)

            if not cells_in_bounds(cells):
                continue
            if touches_occupied(cells, occupied):
                continue

            ship = Ship(ship_id=ship_id, cells=tuple(cells))
            ships.append(ship)
            for c in cells:
                occupied.add(c)
            break
    validate_no_touch(ships)
    return ships

def generate_and_save_bot_ships(path: str = "data/bot_ships.csv", seed: int | None = None) -> List[Ship]:
    ships = generate_bot_ships(seed=seed)
    save_ships_csv(ships, path)
    return ships

