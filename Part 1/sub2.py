# 2430888
# 2436109
# 2425639

import chess


def execute_move(fen, move):
    board = chess.Board(fen)
    move = chess.Move.from_uci(move)
    board.push(move)
    return board.fen()


# Take input from user
fen = input()
move = input()
print(execute_move(fen, move))
