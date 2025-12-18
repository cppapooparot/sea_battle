from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional

from src.utils import Coord


def board_to_str(fog: List[List[str]]) -> str:
    # 10 lines of 10 chars joined with "/"
    return "/".join("".join(row) for row in fog)


def coord_to_str(c: Optional[Coord]) -> str:
    if c is None:
        return ""
    x, y = c
    return f"{x},{y}"


def move_to_str(c: Optional[Coord], result: str) -> str:
    if c is None or not result:
        return ""
    return f"{coord_to_str(c)}:{result}"


def combined_state(fog_vs_bot: List[List[str]], fog_vs_you: List[List[str]]) -> str:
    # P = player's fog vs bot, B = bot's fog vs player
    return f"P={board_to_str(fog_vs_bot)}|B={board_to_str(fog_vs_you)}"


def ensure_game_state_csv(path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.stat().st_size > 0:
        return
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["turn", "player_move", "bot_move", "state"])


def append_turn(
    path: str,
    turn: int,
    player_coord: Optional[Coord],
    player_result: str,
    bot_coord: Optional[Coord],
    bot_result: str,
    fog_vs_bot: List[List[str]],
    fog_vs_you: List[List[str]],
) -> None:
    ensure_game_state_csv(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                turn,
                move_to_str(player_coord, player_result),
                move_to_str(bot_coord, bot_result),
                combined_state(fog_vs_bot, fog_vs_you),
            ]
        )

def reset_game_state_csv(path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["turn", "player_move", "bot_move", "state"])