from __future__ import annotations
from typing import Literal, Optional, Set, List

from src.ship_input import Ship
from dataclasses import dataclass, field
from src.utils import Coord, neighbors_8, neighbors_4
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


def bot_random_shot(rng: Random, fog: List[List[str]]) -> Coord:
    choices: List[Coord] = []
    for y in range(10):
        for x in range(10):
            if fog[y][x] == ".":
                choices.append((x, y))
    if not choices:
        raise RuntimeError("No available shots left.")
    return rng.choice(choices)

def in_bounds(c : Coord, size: int = 10) -> bool:
    x, y = c
    return 0 <= x < size and 0 <= y < size

def is_unshot(fog: List[List[str]], c: Coord) -> bool:
    x, y = c
    return fog[y][x] == "."

def line_candidates(hit_cluster: Set[Coord], fog: List[List[str]]) -> List[Coord]:
    """
    Bot AI logic:
    If we already have >=2 hits, infer orientation and propose next cells at both ends.
    """
    xs = sorted({x for x, _ in hit_cluster})
    ys = sorted({y for _, y in hit_cluster})
    out: List[Coord] = []

    # vertical
    if len(xs) == 1 and len(ys) >= 2:
        x = xs[0]
        y_min, y_max = ys[0], ys[-1]
        c1 = (x, y_min - 1)
        c2 = (x, y_max + 1)
        for c in (c1, c2):
            if in_bounds(c) and is_unshot(fog, c):
                out.append(c)
        return out

    # horizontal
    if len(ys) == 1 and len(xs) >= 2:
        y = ys[0]
        x_min, x_max = xs[0], xs[-1]
        c1 = (x_min - 1, y)
        c2 = (x_max + 1, y)
        for c in (c1, c2):
            if in_bounds(c) and is_unshot(fog, c):
                out.append(c)
        return out

    return []

@dataclass
class BotAI:
    """
    If there is a current hit cluster: try to finish that ship using:
        1) line extension (after we know orientation)
        2) otherwise 4-neighbors around hits
    If no active target: random search.
    """
    rng: Random = field(default_factory=Random)
    hit_cluster: Set[Coord] = field(default_factory=set)
    queue: List[Coord] = field(default_factory=list)

    def choose_shot(self, fog: List[List[str]]) -> Coord:
        if self.hit_cluster:
            for c in line_candidates(self.hit_cluster, fog):
                if c not in self.queue:
                    self.queue.insert(0, c)
        while self.queue:
            c = self.queue.pop(0)
            if in_bounds(c) and is_unshot(fog, c):
                return c
            
        return bot_random_shot(self.rng, fog)
    
    def observe(self, shot: Coord, result: ShotResult, fog: List[List[str]]) -> None:
        if result == "hit":
            self.hit_cluster.add(shot)

            #if no orientation yet
            if not line_candidates(self.hit_cluster, fog):
                for n in neighbors_4(shot):
                    if in_bounds(n) and is_unshot(fog, n) and n not in self.queue:
                        self.queue.append(n)
        elif result == "sunk":
            self.hit_cluster.clear()
            self.queue.clear()
        #miss/repeat do nothing
