from src import utils

def main() -> None:
    board = utils.new_fog_board()
    print(utils.render_board(board, "Demo"))

if __name__ == "__main__":
    main()