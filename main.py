from __future__ import annotations

from pathlib import Path

from src.bot_generation import generate_and_save_bot_ships
from src.gameplay import all_sunk, apply_shot
from src.ship_input import load_ships_csv
from src.utils import new_fog_board, parse_xy, render_board


def main() -> None:
    bot_path = Path("data/bot_ships.csv")

    ships = []
    if bot_path.exists():
        try:
            ships = load_ships_csv(str(bot_path))
        except Exception:
            ships = []

    if not ships:
        generate_and_save_bot_ships(str(bot_path), seed=None)
        ships = load_ships_csv(str(bot_path))

    hits: set[tuple[int, int]] = set()
    fog = new_fog_board()

    print(render_board(fog, "Fog (your shots vs bot)"))
    while True:
        s = input("shot > ").strip().lower()
        if s in ("q", "quit", "exit"):
            break

        try:
            c = parse_xy(s)
        except ValueError as e:
            print(f"Bad input: {e}")
            continue

        result = apply_shot(ships, hits, fog, c, mark_around_sunk=True)
        print("Result:", result)
        print(render_board(fog, "Fog"))

        if all_sunk(ships, hits):
            print("You win. All bot ships sunk.")
            break


if __name__ == "__main__":
    main()