import chess.engine
import random
from reconchess import *
import os
from collections import defaultdict
import numpy as np
import scipy.signal as sp
import platform

# Set stockfish path based on the operating system
if platform.system() == 'Windows':
    stockfish_path = './stockfish-windows-x86-64-avx2.exe'
elif platform.system() == 'Linux':
    stockfish_path = './stockfish-ubuntu-x86-64-avx2'
elif platform.system() == 'Darwin':
    stockfish_path = './stockfish-macos-m1-apple-silicon'
else:
    raise EnvironmentError('Unsupported platform')


class Veru(Player):
    def __init__(self):
        self.possible_fens = set()
        self.color = None
        self.my_piece_captured_square = None
        self.move_count = 0

        # Initialize Stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(
            stockfish_path, setpgrp=True)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.color = color
        self.possible_fens.add(board.fen())
        self.move_count = 0

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        if self.move_count == 0 and self.color == chess.WHITE:
            self.move_count += 1
            return

        self.my_piece_captured_square = capture_square

        if capture_square is None:
            possible_fens = set()

            for fen in self.possible_fens:
                curr_board = chess.Board(fen)

                for move in curr_board.pseudo_legal_moves:
                    curr_board.push(move)
                    possible_fens.add(curr_board.fen())
                    curr_board.pop()

                curr_board.push(chess.Move.null())
                possible_fens.add(curr_board.fen())

            self.possible_fens = possible_fens
            return

        # Filter fens that match the piece missing.
        matching_fens = set()

        for fen in self.possible_fens:
            curr_board = chess.Board(fen)

            for move in curr_board.pseudo_legal_moves:
                if move.to_square == capture_square:
                    curr_board.push(move)
                    matching_fens.add(curr_board.fen())
                    curr_board.pop()

        self.possible_fens = matching_fens

    def choose_sense(
        self,
        sense_actions: List[Square],
        move_actions: List[chess.Move],
        seconds_left: float,
    ) -> Optional[Square]:
        square_entropy = defaultdict(dict)
        fens_to_use = min(10000, len(self.possible_fens))

        for fen in random.sample(list(self.possible_fens), fens_to_use):
            curr_board = chess.Board(fen)

            for square, piece in curr_board.piece_map().items():
                square_entropy[square][piece] = square_entropy[square].get(
                    piece, 0) + 1

        board_entropy = np.zeros((8, 8), dtype=float)

        for square in square_entropy.keys():
            square_row = square // 8
            square_col = square % 8

            entropy = 0
            total_count = sum(square_entropy[square].values())

            for piece, count in square_entropy[square].items():
                prob = count / total_count
                entropy -= prob * np.log2(prob)

            board_entropy[square_row, square_col] = entropy

        entropy_sum = sp.convolve2d(
            board_entropy, np.ones((3, 3), dtype=float), mode="same")

        max_entropy_indices = np.where(
            entropy_sum.flatten() == np.max(entropy_sum))[0]
        # Convert to a 1-D NumPy array
        max_entropy_indices = np.array(max_entropy_indices)

        if len(max_entropy_indices) == 0:
            return None

        # Convert back to Square
        return chess.SquareSet(np.random.choice(max_entropy_indices)).pop()

    def handle_sense_result(self, sense_result: list[tuple[Square, Optional[chess.Piece]]]):
        filtered_fens = set()

        print("Veru Agent")
        print(f"{len(self.possible_fens)} before sensing")

        for fen in self.possible_fens:
            curr_board = chess.Board(fen)
            matching = True

            for location, piece in sense_result:
                if curr_board.piece_at(location) != piece:
                    matching = False
                    break

            if matching:
                filtered_fens.add(fen)

        self.possible_fens = filtered_fens

    def choose_move(self, move_actions: list[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        valid_fens = set()

        for fen in self.possible_fens:
            board = chess.Board(fen)
            if all(move in move_actions for move in board.pseudo_legal_moves):
                valid_fens.add(fen)

        self.possible_fens = valid_fens

        time_limit = min(seconds_left, 10)  # adjust the time limit as needed
        move_counts = {}

        print(f"Possible: {len(self.possible_fens)} fens")

        if len(self.possible_fens) > 10000:
            self.possible_fens = set(random.sample(
                list(self.possible_fens), 10000))

        # Make sure not divide by 0
        if len(self.possible_fens) == 0:
            print("No possible fens")
            return None

        time_limit_per_fen = time_limit / len(self.possible_fens)

        print(f"Exploring: {len(self.possible_fens)} fens")
        print()

        for fen in self.possible_fens:
            curr_board = chess.Board(fen)
            enemy_king_square = curr_board.king(not self.color)

            if enemy_king_square:
                enemy_king_attackers = curr_board.attackers(
                    self.color, enemy_king_square)

                if enemy_king_attackers:
                    attacker_square = enemy_king_attackers.pop()
                    move = chess.Move(attacker_square, enemy_king_square)
                    move_counts[move] = move_counts.get(move, 0) + 1

                    if move in move_actions:
                        return move

            try:
                move = self.engine.play(
                    curr_board, chess.engine.Limit(time=time_limit_per_fen))
                move_counts[move.move] = move_counts.get(move.move, 0) + 1
            except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                self.engine = chess.engine.SimpleEngine.popen_uci(
                    stockfish_path, setpgrp=True)
            except chess.IllegalMoveError:
                pass

        if not move_counts:
            return None

        most_popular_count = max(move_counts.values())
        best_moves = [move for move, count in move_counts.items()
                      if count == most_popular_count]
        best_move = np.random.choice(best_moves)
        return best_move

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        updated_fens = set()

        for fen in self.possible_fens:
            curr_board = chess.Board(fen)

            if taken_move is None:
                # Handle invalid move
                if requested_move not in curr_board.pseudo_legal_moves:
                    curr_board.push(chess.Move.null())
                    curr_board.color = not self.color
                    updated_fens.add(curr_board.fen())
            elif taken_move in curr_board.pseudo_legal_moves:
                # Handle valid move
                if not captured_opponent_piece or (captured_opponent_piece and curr_board.is_capture(taken_move)):
                    curr_board.push(taken_move)
                    updated_fens.add(curr_board.fen())

        self.possible_fens = updated_fens

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        self.engine.quit()
