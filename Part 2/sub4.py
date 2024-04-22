# 2430888
# 2436109
# 2425639

import chess


def parse_sense(sense_str):
    sense_list = sense_str.split(";")
    sense_dict = {}
    for s in sense_list:
        info_pair = s.split(":")
        if info_pair[1] == "?":
            info_pair[1] = None
        sense_dict[info_pair[0]] = info_pair[1]
    return sense_dict


def print_fen_states(states):
    states.sort()  # Sort the states alphabetically
    for fen in states:
        print(fen)


def filter_valid_states(states, sense_dict):
    valid_states = []
    for fen in states:
        valid = True
        board = chess.Board(fen)
        for square, piece in sense_dict.items():
            state_piece = board.piece_at(chess.parse_square(square))
            if piece is not None:
                piece = chess.Piece.from_symbol(piece)
            if state_piece != piece:
                valid = False
                break
        if valid:
            valid_states.append(fen)
    return valid_states


def main():
    num_states = int(input())
    states = [input() for i in range(num_states)]
    window = input()

    sense_dict = parse_sense(window)
    valid_states = filter_valid_states(states, sense_dict)
    print_fen_states(valid_states)


if __name__ == "__main__":
    main()
