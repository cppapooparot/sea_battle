from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Tuple

from src.utils import Coord, neighbors_8, parse_xy

SHIP_SIZES: List[int] = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

@dataclass(frozen=True)
class Ship:
    ship_id: int
    cells: Tuple[Coord, ...]

    @property
    def size(self) -> int:
        return len(self.cells)
    
def cells_from_segment(a: Coord, b: Coord) ->List[Coord]:
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