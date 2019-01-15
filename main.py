import argparse
import datetime
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import os

from algos import CFR, Exp3P
from games import RockPaperScissors, TicTacToe
from utils import compute_normalized_entropy, compute_RPS_expected_gains, compute_RPS_players_utility

parser = argparse.ArgumentParser()
parser.add_argument('--game', required=True,
                    help='game: RPS or TTT')
parser.add_argument('--algo', required=True,
                    help='algorithm: Exp3P or CFR')
parser.add_argument('--iter', type=int, default='1000',
                    help='number of policy updates (default: 1000)')
parser.add_argument('--eta', type=float, default=0,
                    help='η parameter for Exp3P')
parser.add_argument('--gamma', type=float, default=0,
                    help='γ parameter for Exp3P')
parser.add_argument('--beta', type=float, default=0,
                    help='β parameter for Exp3P')
parser.add_argument('--nb-seeds', type=int, default=5,
                    help='number of seeds to average the results on (default: 5)')
args = parser.parse_args()

assert args.game in ['RPS', 'TTT']
assert args.algo in ['Exp3P', 'CFR']

if args.algo == 'Exp3P':
    hyper_params = 'η{}_γ{}_β{}'.format(args.eta, args.gamma, args.beta)
elif args.algo == 'CFR':
    hyper_params = ''
writer_path = 'storage/{}_{}_N{}_{}'.format(args.game, args.algo, args.iter, hyper_params)

iters = np.arange(1, args.iter+1)

if args.game == 'RPS':
    game = RockPaperScissors()

    if args.algo == 'Exp3P':
        # For plots
        N_entropiess_0 = []
        N_entropiess_1 = []
        E_gainss_0 = []
        E_gainss_1 = []
        regretss_0 = []
        regretss_1 = []

        for seed in tqdm(range(args.nb_seeds)):
            np.random.seed(seed)

            actions = game.init_h.I.available_actions
            p0 = Exp3P(actions, args.eta, args.gamma, args.beta, init_weights="hot")
            p1 = Exp3P(actions, args.eta, args.gamma, args.beta, init_weights="hot")

            # For plots
            N_entropies_0 = []
            N_entropies_1 = []
            E_gains_0 = []
            E_gains_1 = []
            regrets_0 = []
            regrets_1 = []
            S0 = {a: 0 for a in range(3)}
            S1 = {a: 0 for a in range(3)}

            for i in tqdm(iters):
                a0 = p0.play()
                a1 = p1.play()
                h = game.init_h.next(a0).next(a1)
                u0 = game.u(h, 0)
                p0.analyze_feedback(u0)
                p1.analyze_feedback(-u0)

                # For plots
                π0 = p0.π
                π1 = p1.π
                E_gain_0, E_gain_1 = compute_RPS_expected_gains(π0, π1)
                E_gains_0.append(E_gain_0)
                E_gains_1.append(E_gain_1)
                N_entropy_0 = compute_normalized_entropy(π0)
                N_entropy_1 = compute_normalized_entropy(π1)
                N_entropies_0.append(N_entropy_0)
                N_entropies_1.append(N_entropy_1)
                u0, u1 = compute_RPS_players_utility(a0, a1)
                S0 = {a: S0[a] + u0[a] - u0[a0] for a in range(3)}
                S1 = {a: S1[a] + u1[a] - u1[a1] for a in range(3)}
                regret_0 = 1/i * max([S0[a] for a in range(3)])
                regret_1 = 1/i * max([S1[a] for a in range(3)])
                regrets_0.append(regret_0)
                regrets_1.append(regret_1)

            # For plots
            N_entropiess_0.append(N_entropies_0)
            N_entropiess_1.append(N_entropies_1)
            E_gainss_0.append(E_gains_0)
            E_gainss_1.append(E_gains_1)
            regretss_0.append(regrets_0)
            regretss_1.append(regrets_1)

        # For plots
        os.makedirs(writer_path, exist_ok=True)
        plt.plot(iters, np.mean(N_entropiess_0, axis=0))
        plt.savefig(writer_path + "/N_entropy_0")
        plt.clf()
        plt.plot(iters, np.mean(N_entropiess_1, axis=0))
        plt.savefig(writer_path + "/N_entropy_1")
        plt.clf()
        plt.plot(iters, np.mean(E_gainss_0, axis=0))
        plt.savefig(writer_path + "/E_gain_0")
        plt.clf()
        plt.plot(iters, np.mean(E_gainss_1, axis=0))
        plt.savefig(writer_path + "/E_gain_1")
        plt.clf()
        plt.plot(iters, np.mean(regretss_0, axis=0))
        plt.savefig(writer_path + "/regret_0")
        plt.clf()
        plt.plot(iters, np.mean(regretss_1, axis=0))
        plt.savefig(writer_path + "/regret_1")
        plt.clf()

    elif args.algo == 'CFR':
        cfr = CFR(game, init_policies="hot")

        for i in tqdm(iters):
            cfr.update_policies()

            # For plots
            π0 = cfr.σ[0]
            π1 = cfr.σ[1]