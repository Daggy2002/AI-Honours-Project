# 2430888
# 2436109
# 2425639

import chess.engine
import random
from reconchess import *
import os

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'


class RandomSensingOld(Player):
    def __init__(self):
        self.possible_boards = set()

        # Initialize Stockfish engine
        # stockfish_path = '/opt/stockfish/stockfish'
        # stockfish_path = './stockfish-macos-m1-apple-silicon'
        stockfish_path = os.environ[STOCKFISH_ENV_VAR]
        self.engine = chess.engine.SimpleEngine.popen_uci(
            stockfish_path, setpgrp=True)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.color = color
        self.possible_boards = {board.fen()}

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        new_possible_boards = set()
        for board_fen in self.possible_boards:
            board = chess.Board(board_fen)
            for move in board.legal_moves:
                if board.is_capture(move) == captured_my_piece:
                    new_board = board.copy()
                    new_board.push(move)
                    new_possible_boards.add(new_board.fen())
        self.possible_boards = new_possible_boards

    def choose_sense(self, sense_actions: list[Square], move_actions: list[chess.Move], seconds_left: float) -> Optional[Square]:
        # Convert integers to Square objects and filter for sense actions within the board
        valid_sense_actions = [
            sq for sq in (chess.Square(s) for s in sense_actions)
            # Adjust boundaries to ensure 3x3 sensing region stays within the board
            if 1 <= chess.square_rank(sq) <= 6 and 1 <= chess.square_file(sq) <= 6
        ]

        if valid_sense_actions:
            return random.choice(valid_sense_actions)
        else:
            return None  # No valid sense actions within the bounds

    def handle_sense_result(self, sense_result: list[tuple[Square, Optional[chess.Piece]]]):
        new_possible_boards = set()
        for board_fen in self.possible_boards:
            board = chess.Board(board_fen)
            valid = True
            for sense_square, piece in sense_result:
                if board.piece_at(sense_square) != piece:
                    valid = False
                    break
            if valid:
                new_possible_boards.add(board_fen)
        self.possible_boards = new_possible_boards

    def choose_move(self, move_actions: list[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        if not self.possible_boards:
            return None

        num_boards = len(self.possible_boards)
        if num_boards > 10000:
            self.possible_boards = set(random.sample(
                list(self.possible_boards), 10000))

        stockfish_time_per_board = 10 / len(self.possible_boards)

        print(f"Number of sample boards: {len(self.possible_boards)}")

        # Initialize scores for all legal moves
        best_moves = {move: 0 for move in move_actions}
        for board_fen in self.possible_boards:
            board = chess.Board(board_fen)
            board.turn = self.color
            board.clear_stack()
            try:
                result = self.engine.play(
                    board, chess.engine.Limit(time=stockfish_time_per_board))
                best_move = result.move
                if best_move in best_moves:  # Only increment score if move is legal
                    best_moves[best_move] += 1
            except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                pass

        if best_moves:
            most_frequent_move, _ = max(
                best_moves.items(), key=lambda item: item[1])
            return most_frequent_move
        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        new_possible_boards = set()
        for board_fen in self.possible_boards:
            board = chess.Board(board_fen)
            if taken_move in board.legal_moves:
                new_board = board.copy()
                new_board.push(taken_move)
                new_possible_boards.add(new_board.fen())
        self.possible_boards = new_possible_boards

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        self.engine.quit()
