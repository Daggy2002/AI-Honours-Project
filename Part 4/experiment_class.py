import os
import re
from tqdm import tqdm


class Experiment:
    def __init__(self, agent, enemy, trials):
        self.trials = trials
        self.total = 0
        self.wins = 0
        self.__command_white = "rc-bot-match " + agent + " " + enemy
        self.__command_black = "rc-bot-match " + enemy + " " + agent

    def __run_single_trial(self, turn):
        command = self.__command_white if turn else self.__command_black
        win_condition = "w" if turn else "b"
        output = os.popen(command).read()
        pos = re.search("Winner: ", output).span()[1]
        winner = output[pos]

        self.total += 1
        if winner == win_condition:
            self.wins += 1

    def __print_results(self):
        print(
            "Wins: ",
            self.wins,
            "/",
            self.total,
            "\nWin Rate:",
            round(self.wins / self.total, 2),
            "%",
        )

    def run_experiment(self):
        turn = True
        for i in tqdm(range(self.trials), desc="Running trials"):
            self.__run_single_trial(turn)
            turn = not turn
        self.__print_results()
