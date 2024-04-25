# 2430888
# 2436109
# 2425639

import chess
import chess.engine


def move_selection(fen):
    # Create a chess board from the FEN string
    board = chess.Board(fen)

    # Get the square of the opposing king
    opposing_king_square = board.king(not board.turn)

    # Check if the opposing king is attacked
    if board.is_attacked_by(board.turn, opposing_king_square):
        # If yes, capture the opposing king
        move = find_capturing_move(board, board.turn)
        return move.uci() if move else None

    # Otherwise, ask Stockfish for a move
    engine = chess.engine.SimpleEngine.popen_uci(
        './stockfish-macos-m1-apple-silicon', setpgrp=True)
    result = engine.play(board, chess.engine.Limit(time=0.5))
    engine.quit()

    return result.move.uci()


def find_capturing_move(board, color):
    # Iterate through all possible moves
    for move in board.legal_moves:
        board.push(move)
        opposing_king_square = board.king(not color)
        if opposing_king_square is None:
            # The opposing king was captured
            board.pop()
            return move
        board.pop()

    return None


# Take the FEN string as input
fen = input()
print(move_selection(fen))
