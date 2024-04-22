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


def filter_moves_by_capture(fen, moves, capture_square):
    board = chess.Board(fen)

    next_states = []

    # Iterate over moves
    for move in moves:
        move_obj = chess.Move.from_uci(move)
        # Check if the move captures a piece
        if board.is_capture(move_obj):
            # Check if the capture occurs on the specified square
            if chess.square_name(move_obj.to_square) == capture_square:
                # Apply the move to the board
                board_copy = board.copy()
                board_copy.push(move_obj)
                next_states.append(board_copy.fen())

    # Sort the next states alphabetically
    next_states.sort()
    return next_states


# Take input from the user
fen = input()
capture_square = input()

# Generate all possible moves
all_moves = generate_next_moves(fen)

# Filter moves by capture on the specified square
next_states = filter_moves_by_capture(fen, all_moves, capture_square)

# Print the next possible states
for state in next_states:
    print(state)
