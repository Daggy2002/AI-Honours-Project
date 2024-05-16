import re


def summarize_results(text):
    # Initialize variables to store the cumulative results
    total_completed_games = 0
    troutbot_wins = 0
    troutbot_white_wins = 0
    troutbot_black_wins = 0
    troutbot_failed_games = 0
    improved_agent_wins = 0
    improved_agent_white_wins = 0
    improved_agent_black_wins = 0
    improved_agent_failed_games = 0

    # Split the text into lines
    lines = text.split("\n")

    # Iterate through each line and extract the relevant information
    for line in lines:
        if "Completed games" in line:
            total_completed_games += int(line.split(":")[1].strip())

        if "TroutBot wins" in line:
            match = re.search(
                r"TroutBot wins: (\d+) \(white wins: (\d+), black wins: (\d+)\)", line)
            if match:
                troutbot_wins += int(match.group(1))
                troutbot_white_wins += int(match.group(2))
                troutbot_black_wins += int(match.group(3))

        if "Failed games" in line and "TroutBot" in line:
            failed_games = re.search(r"Failed games: (\d+)", line)
            if failed_games:
                troutbot_failed_games += int(failed_games.group(1))

        if "ImprovedAgent wins" in line:
            match = re.search(
                r"ImprovedAgent wins: (\d+) \(white wins: (\d+), black wins: (\d+)\)", line)
            if match:
                improved_agent_wins += int(match.group(1))
                improved_agent_white_wins += int(match.group(2))
                improved_agent_black_wins += int(match.group(3))

        if "Failed games" in line and "ImprovedAgent" in line:
            failed_games = re.search(r"Failed games: (\d+)", line)
            if failed_games:
                improved_agent_failed_games += int(failed_games.group(1))

    # Print the summarized results
    print(f"Total completed games: {total_completed_games}")
    print(
        f"TroutBot wins: {troutbot_wins} (white wins: {troutbot_white_wins}, black wins: {troutbot_black_wins})")
    print(f"TroutBot failed games: {troutbot_failed_games}")
    print(
        f"ImprovedAgent wins: {improved_agent_wins} (white wins: {improved_agent_white_wins}, black wins: {improved_agent_black_wins})")
    print(f"ImprovedAgent failed games: {improved_agent_failed_games}")
    print()

    # Win rate
    print(f"TroutBot win rate: {troutbot_wins/total_completed_games}")
    print(
        f"ImprovedAgent win rate: {improved_agent_wins/total_completed_games}")


# Take in the textfile
with open("5000_final.txt", "r") as file:
    text = file.read()

# Call the function to summarize the results
summarize_results(text)
