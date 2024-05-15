import json
import traceback
from datetime import datetime
import chess
from reconchess import LocalGame, play_local_game
import matplotlib.pyplot as plt


def play_double_round_robin_tournament(bots, num_tournaments):
    bot_names = []
    for i, bot in enumerate(bots):
        bot_type = type(bot).__name__
        bot_name = f"{bot_type}_{i}"
        bot_names.append(bot_name)

    tournament_results = []

    for tournament_num in range(num_tournaments):
        print(f"\nStarting Tournament {tournament_num + 1}")
        num_bots = len(bots)
        bot_results = {bot_name: {"wins": 0, "draws": 0, "rounds": [
        ], "wins_white": 0, "wins_black": 0, "failed": 0} for bot_name in bot_names}

        # Total rounds in a single RR tournament
        total_rounds = (num_bots * (num_bots - 1)) // 2
        current_round = 1

        for i in range(num_bots):
            for j in range(i + 1, num_bots):
                bot1 = bots[i]
                bot2 = bots[j]
                bot1_name = bot_names[i]
                bot2_name = bot_names[j]
                bot1_wins = 0
                bot2_wins = 0
                draws = 0
                round_results = []

                print(
                    f"\nRound {current_round}/{total_rounds}: {bot1_name} vs {bot2_name}")

                # Play as white and black
                for color in [chess.WHITE, chess.BLACK]:
                    game = LocalGame()
                    try:
                        if color == chess.WHITE:
                            white_bot, black_bot = bot1, bot2
                        else:
                            white_bot, black_bot = bot2, bot1

                        winner_color, _, _ = play_local_game(
                            white_bot, black_bot, game=game)
                        if winner_color is not None:
                            if winner_color == chess.WHITE:
                                bot1_wins += 1
                                bot_results[bot1_name]["wins_white"] += 1
                                round_results.append({
                                    "round": current_round,
                                    "white_bot": bot1_name,
                                    "black_bot": bot2_name,
                                    "winner": bot1_name
                                })
                            else:
                                bot2_wins += 1
                                bot_results[bot2_name]["wins_black"] += 1
                                round_results.append({
                                    "round": current_round,
                                    "white_bot": bot1_name,
                                    "black_bot": bot2_name,
                                    "winner": bot2_name
                                })
                        else:
                            draws += 1
                            round_results.append({
                                "round": current_round,
                                "white_bot": bot1_name,
                                "black_bot": bot2_name,
                                "winner": "Draw"
                            })
                    except Exception as e:
                        traceback.print_exc()
                        bot_results[bot2_name]["failed"] += 1
                        round_results.append({
                            "round": current_round,
                            "white_bot": bot1_name,
                            "black_bot": bot2_name,
                            "winner": bot2_name  # Assign win to the other bot
                        })

                bot_results[bot1_name]["wins"] += bot1_wins
                bot_results[bot2_name]["wins"] += bot2_wins
                bot_results[bot1_name]["draws"] += draws
                bot_results[bot2_name]["draws"] += draws
                bot_results[bot1_name]["rounds"].extend(round_results)
                bot_results[bot2_name]["rounds"].extend(round_results)

                current_round += 1  # Increment the round count

        tournament_results.append(bot_results)

    # Save tournament results to a JSON file
    with open("tournament_results.json", "w") as f:
        json.dump(tournament_results, f, indent=2)

    # Save the statistics for each bot as a table image
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    column_labels = ["Bot", "Tournaments Won", "Total Wins",
                     "Wins as White", "Wins as Black", "Draws", "Failed Games"]
    table_data = []
    for bot_name in bot_names:
        total_wins = 0
        total_wins_white = 0
        total_wins_black = 0
        total_draws = 0
        total_failed = 0
        tournament_wins = 0
        for result in tournament_results:
            total_wins += result[bot_name]["wins"]
            total_wins_white += result[bot_name]["wins_white"]
            total_wins_black += result[bot_name]["wins_black"]
            total_draws += result[bot_name]["draws"]
            total_failed += result[bot_name]["failed"]
            if result[bot_name]["wins"] == max(result[bot_name]["wins"] for bot_name in bot_names):
                tournament_wins += 1
        table_data.append([bot_name, tournament_wins, total_wins,
                          total_wins_white, total_wins_black, total_draws, total_failed])

    table = ax.table(
        cellText=table_data,
        colLabels=column_labels,
        loc='center',
        cellLoc='center',
        rowLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    plt.savefig("tournament_stats.png", bbox_inches='tight')


if __name__ == '__main__':
    from TroutBot import TroutBot
    from ImprovedAgent import ImprovedAgent
    from RandomSensing import RandomSensing
    from reconchess.bots.random_bot import RandomBot

    # Choose any bots for the tournament
    bots = [RandomBot(), RandomBot(), RandomBot(), RandomBot()]
    num_tournaments = 1  # Change this value to the desired number of tournaments

    tournament_results = play_double_round_robin_tournament(
        bots, num_tournaments)
