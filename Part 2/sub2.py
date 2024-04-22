# 2430888
# 2436109
# 2425639

import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle


def generate_next_moves(fen):

    board = chess.Board(fen)

    all_moves = []

    # 1. Null move
    all_moves.append('0000')

    # 2. Regular pseudolegal moves (including promotions)
    all_moves.extend(str(move) for move in board.pseudo_legal_moves)

    # 3. Castling moves (considering RBC rules)
    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move):
            all_moves.append(str(move))

    # Remove duplicate moves
    all_moves = list(set(all_moves))

    # Sort moves alphabetically for consistent output
    return sorted(all_moves)


# Take input from user
fen = input()
appliedMovesArray = []
for move in generate_next_moves(fen):
    # Apply the move to the board
    board = chess.Board(fen)
    move = chess.Move.from_uci(move)
    board.push(move)
    appliedMovesArray.append(board.fen())

# Sort the applied moves array in alphabetical order
appliedMovesArray.sort()
for fen in appliedMovesArray:
    print(fen)
