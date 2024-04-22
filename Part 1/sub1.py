# 2430888
# 2436109
# 2425639

import chess


def print_board(fen):
    board = chess.Board(fen)
    print(board)


# Take input from user
fen = input()
print_board(fen)
