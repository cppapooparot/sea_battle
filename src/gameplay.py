from __future__ import annotations
from typing import Literal, Optional, Set, List

from src.ship_input import Ship
from dataclasses import dataclass, field
from src.utils import Coord, neighbors_8, neighbors_4
from src.ship_input import Ship
from random import Random

ShotResult = Literal["repeat", "miss", "hit", "sunk"]

def find_ship_at(ships: List[Ship], c: Coord) -> Optional[Ship]:
    # return the ship that is in Coord c or none if c is empty
    for ship in ships:
        if c in ship.cells:
            return ship
    return None

def is_sunk(ship: Ship, hits: Set[Coord]) -> bool:
    # return true if every cell of ship was destroyed
    return all(cell in hits for cell in ship.cells)

def apply_shot(ships: List[Ship], hits: Set[Coord], fog: List[List[str]], c: Coord, *, mark_around_sunk: bool = True) -> ShotResult:
    x, y = c
    # if already shot
    if fog[y][x] in ("o", "x"):
        return "repeat"

    ship = find_ship_at(ships, c)

    # miss
    if ship is None:
        fog[y][x] = "o"
        return "miss"

    # hit
    hits.add(c)
    fog[y][x] = "x"

    # if ship is sunk, optionally mark surrounding cells as misses
    if is_sunk(ship, hits):
        if mark_around_sunk:
            for cell in ship.cells:
                for nx, ny in neighbors_8(cell):
                    if fog[ny][nx] == ".":
                        fog[ny][nx] = "o"
        return "sunk"

    return "hit"

def all_sunk(ships: List[Ship], hits: Set[Coord]) -> bool:
    # return true if every ship in ships is sunk
    return all(is_sunk(ship, hits) for ship in ships)
