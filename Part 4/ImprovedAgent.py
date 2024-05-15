import chess.engine
import random
from reconchess import *
import os
from collections import defaultdict
import numpy as np
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

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 10  # You may want to assign a higher value for the king
}


def evaluate_region(board, square, color):
    value = 0
    for offset in [-9, -8, -7, -1, 1, 7, 8, 9]:
        neighbor = square + offset
        neighbor_rank = chess.square_rank(neighbor)
        neighbor_file = chess.square_file(neighbor)
        if 0 <= neighbor_rank < 8 and 0 <= neighbor_file < 8:
            piece = board.piece_at(neighbor)
            if piece is not None and piece.color != color:
                value += piece_values.get(piece.piece_type, 0)
    return value


class ImprovedAgent(Player):
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

    def choose_sense(self, sense_actions: list[Square], move_actions: list[chess.Move], seconds_left: float) -> Optional[Square]:
        sampled_fens = list(self.possible_fens)
        if len(sampled_fens) > 10000:
            sampled_fens = random.sample(sampled_fens, 10000)

        attacked_king_count = 0
        attacker_square = None

        for fen in sampled_fens:
            board = chess.Board(fen)
            our_king_square = board.king(self.color)

            if our_king_square:
                our_king_attackers = board.attackers(
                    not self.color, our_king_square)

                if our_king_attackers:
                    attacked_king_count += 1
                    if attacker_square is None:
                        attacker_square = our_king_attackers.pop()

        if attacked_king_count > len(sampled_fens) // 2 and attacker_square in sense_actions:
            return attacker_square

        if self.my_piece_captured_square is not None and self.my_piece_captured_square in sense_actions:
            # Get the rank and file of the captured square
            rank = chess.square_rank(self.my_piece_captured_square)
            file = chess.square_file(self.my_piece_captured_square)
            # Adjust rank and file as per the rules
            if rank == 7:
                rank = 6
            elif rank == 0:
                rank = 1
            if file == 0:
                file = 1
            elif file == 7:
                file = 6
            # Convert rank and file back to the integer representation of the square
            return chess.square(file, rank)

        max_value = 0
        best_square = None

        for fen in sampled_fens:
            board = chess.Board(fen)
            for square in sense_actions:
                if 1 <= chess.square_rank(square) <= 6 and 1 <= chess.square_file(square) <= 6:
                    region_value = evaluate_region(board, square, self.color)
                    if region_value > max_value:
                        max_value = region_value
                        best_square = square

        return best_square

    def handle_sense_result(self, sense_result: list[tuple[Square, Optional[chess.Piece]]]):
        filtered_fens = set()

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
