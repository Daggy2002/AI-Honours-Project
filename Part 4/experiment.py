import experiment_class as ec

bots = {
    "random": "reconchess.bots.random_bot",
    "trout": "TroutBot.py",
    "attack": "reconchess.bots.attacker_bot",
    "RandomSensing": "RandomSensing.py",
    "Veru": "veru.py",
    "ImprovedAgent": "ImprovedAgent.py"
}


def run(agent, enemy, trials):
    agent = bots[agent]
    enemy = bots[enemy]
    ec.Experiment(agent, enemy, 2 * trials).run_experiment()


def main():
    num_trials = 10

    agent = "ImprovedAgent"
    enemy = "Veru"

    run(agent, enemy, num_trials)


if __name__ == "__main__":
    main()
