import traceback
from datetime import datetime
import chess
from reconchess import LocalGame, play_local_game


def play_round_robin_tournament(bots, num_tournaments=1, num_games=1):
    for tournament in range(num_tournaments):
        print(f"Tournament {tournament + 1}:")
        num_bots = len(bots)
        bot_results = {bot: {"wins": 0, "draws": 0} for bot in bots}

        for i in range(num_bots):
            for j in range(i + 1, num_bots):
                bot1 = bots[i]
                bot2 = bots[j]
                bot1_wins = 0
                bot2_wins = 0
                draws = 0

                for game_index in range(num_games):
                    game = LocalGame()
                    try:
                        if game_index % 2 == 0:
                            white_bot, black_bot = bot1, bot2
                        else:
                            white_bot, black_bot = bot2, bot1

                        winner_color, _, _ = play_local_game(
                            white_bot, black_bot, game=game)

                        if winner_color is not None:
                            if winner_color == chess.WHITE:
                                bot1_wins += 1
                            else:
                                bot2_wins += 1
                        else:
                            draws += 1
                    except Exception as e:
                        traceback.print_exc()

                bot_results[bot1]["wins"] += bot1_wins
                bot_results[bot2]["wins"] += bot2_wins
                bot_results[bot1]["draws"] += draws
                bot_results[bot2]["draws"] += draws

                # Reverse the bots for the next round
                bots.reverse()

        print("Tournament Results:")
        for bot, result in bot_results.items():
            total_wins = result["wins"]
            total_draws = result["draws"]
            total_games = num_games * (num_bots - 1)
            win_ratio = total_wins / total_games
            draw_ratio = total_draws / total_games
            print(f"{type(bot).__name__}: Wins: {total_wins}, Draws: {total_draws}, Win Ratio: {win_ratio:.2f}, Draw Ratio: {draw_ratio:.2f}")


if __name__ == '__main__':
    from TroutBot import TroutBot
    from ImprovedAgent import ImprovedAgent
    from RandomSensing import RandomSensing
    from reconchess.bots.random_bot import RandomBot

    # Choose any bots for the tournament
    bots = [TroutBot(), ImprovedAgent(), RandomSensing(), RandomBot()]

    num_games = 1
    num_tournaments = 1
    play_round_robin_tournament(bots, num_tournaments, num_games)
