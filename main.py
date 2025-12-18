from __future__ import annotations

from src.bot_generation import generate_and_save_bot_ships
from src.game_state import append_turn, reset_game_state_csv
from src.gameplay import BotAI, all_sunk, apply_shot
from src.ship_input import load_ships_csv, run_ship_input
from src.utils import new_fog_board, parse_xy, render_board


def render_side_by_side(left: str, right: str, gap: int = 6) -> str:
    lns_l = left.splitlines()
    lns_r = right.splitlines()
    w = max((len(s) for s in lns_l), default=0)
    n = max(len(lns_l), len(lns_r))
    lns_l += [""] * (n - len(lns_l))
    lns_r += [""] * (n - len(lns_r))
    pad = " " * gap
    return "\n".join(lns_l[i].ljust(w) + pad + lns_r[i] for i in range(n))


def main() -> None:
    # Prepare empty fogs (requested: show empty boards before first input)
    fog_vs_bot = new_fog_board()
    fog_vs_you = new_fog_board()

    print(
        render_side_by_side(
            render_board(fog_vs_bot, "Your shots vs bot"),
            render_board(fog_vs_you, "Bot shots vs you"),
        )
    )

    # New game: reset move log
    reset_game_state_csv("data/game_state.csv")
    turn = 0

    # Player inputs ships
    run_ship_input("data/player_ships.csv")

    # Bot generates ships
    generate_and_save_bot_ships("data/bot_ships.csv", seed=None)

    # Load fleets
    player_ships = load_ships_csv("data/player_ships.csv")
    if not player_ships:
        raise SystemExit("Player ships file is empty after input. Aborting.")

    bot_ships = load_ships_csv("data/bot_ships.csv")
    if not bot_ships:
        raise SystemExit("Bot ships file is empty after generation. Aborting.")

    # Game state
    you_hits: set[tuple[int, int]] = set()
    bot_hits: set[tuple[int, int]] = set()
    bot = BotAI()

    print("Game start. Enter shots as 'xy' (example 34). 'q' to quit.")

    while True:
        # Show both fogs side-by-side before player input
        print(
            render_side_by_side(
                render_board(fog_vs_bot, "Your shots vs bot"),
                render_board(fog_vs_you, "Bot shots vs you"),
            )
        )

        # --- Player turn ---
        s = input("your shot > ").strip().lower()
        if s in ("q", "quit", "exit"):
            break

        try:
            player_c = parse_xy(s)
        except ValueError as e:
            print(f"Bad input: {e}")
            continue

        player_r = apply_shot(bot_ships, you_hits, fog_vs_bot, player_c, mark_around_sunk=True)
        print("You:", player_r)

        # If player ended game, bot doesn't shoot; still write the turn
        if all_sunk(bot_ships, you_hits):
            turn += 1
            append_turn(
                "data/game_state.csv",
                turn,
                player_c,
                player_r,
                None,
                "",
                fog_vs_bot,
                fog_vs_you,
            )
            print(
                render_side_by_side(
                    render_board(fog_vs_bot, "Your shots vs bot"),
                    render_board(fog_vs_you, "Bot shots vs you"),
                )
            )
            print("You win.")
            break

        # --- Bot turn ---
        bot_c = bot.choose_shot(fog_vs_you)
        bot_r = apply_shot(player_ships, bot_hits, fog_vs_you, bot_c, mark_around_sunk=True)
        bot.observe(bot_c, bot_r, fog_vs_you)
        print(f"Bot shot {bot_c} -> {bot_r}")

        # Log after both moves
        turn += 1
        append_turn(
            "data/game_state.csv",
            turn,
            player_c,
            player_r,
            bot_c,
            bot_r,
            fog_vs_bot,
            fog_vs_you,
        )

        if all_sunk(player_ships, bot_hits):
            print(
                render_side_by_side(
                    render_board(fog_vs_bot, "Your shots vs bot"),
                    render_board(fog_vs_you, "Bot shots vs you"),
                )
            )
            print("You lose.")
            break


if __name__ == "__main__":
    main()
