import traceback
from datetime import datetime
import chess
from reconchess import LocalGame, play_local_game


def main(bot1, bot2):
    bot1_name = type(bot1).__name__
    bot2_name = type(bot2).__name__
    num_games = 10
    bot1_wins = 0
    bot2_wins = 0
    bot1_white_wins = 0
    bot1_black_wins = 0
    bot2_white_wins = 0
    bot2_black_wins = 0
    draws = 0
    completed_games = 0
    bot1_failed_games = 0
    bot2_failed_games = 0

    for i in range(num_games):
        game = LocalGame()
        try:
            if i % 2 == 0:
                white_bot, black_bot = bot1, bot2
            else:
                white_bot, black_bot = bot2, bot1

            winner_color, win_reason, history = play_local_game(
                white_bot, black_bot, game=game
            )

            winner = 'Draw'
            if winner_color is not None:
                winner = chess.COLOR_NAMES[winner_color]
                if type(white_bot) == type(bot1):
                    bot1_wins += 1
                    if winner_color == chess.WHITE:
                        bot1_white_wins += 1
                    else:
                        bot1_black_wins += 1
                else:
                    bot2_wins += 1
                    if winner_color == chess.WHITE:
                        bot2_white_wins += 1
                    else:
                        bot2_black_wins += 1
            else:
                draws += 1

            completed_games += 1
            print(f'Game {i + 1}: Winner - {winner}')
        except Exception as e:
            if type(white_bot) == type(bot1):
                bot1_failed_games += 1
            else:
                bot2_failed_games += 1
            traceback.print_exc()
            game.end()
            print('Game Over: ERROR')

        history = game.get_game_history()
        timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
        replay_path = f'replays/{bot1_name}_vs_{bot2_name}_{timestamp}.json'
        print(f'Saving replay to {replay_path}...')
        history.save(replay_path)

    total_completed_games = completed_games
    bot1_win_ratio = bot1_wins / total_completed_games
    bot2_win_ratio = bot2_wins / total_completed_games
    draw_ratio = draws / total_completed_games

    print(f'\nResults after {num_games} games:')
    print(f'Completed games: {total_completed_games}')
    print(f'{bot1_name} win ratio: {bot1_win_ratio:.2f} (White: {bot1_white_wins}, Black: {bot1_black_wins}), Failed games: {bot1_failed_games}')
    print(f'{bot2_name} win ratio: {bot2_win_ratio:.2f} (White: {bot2_white_wins}, Black: {bot2_black_wins}), Failed games: {bot2_failed_games}')
    print(f'Draw ratio: {draw_ratio:.2f}')


if __name__ == '__main__':
    from TroutBot import TroutBot
    from ImprovedAgent import ImprovedAgent
    from veru import Veru

    # Choose any two bots from the three available bots
    bot1 = TroutBot()
    bot2 = ImprovedAgent()

    main(bot1, bot2)
