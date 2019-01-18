import argparse
import datetime
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import os

from games import NormalFormGame, TicTacToe
from utils import load_MAB_algo, smooth, compute_NFG_KL, compute_NFG_expected_gains, compute_NFG_players_utility

parser = argparse.ArgumentParser()
parser.add_argument('--game', required=True,
                    help='game: NFG or TTT')
parser.add_argument('--algo', required=True,
                    help='algorithm: Exp3P or CFR')
parser.add_argument('--iters', type=int, default='10000',
                    help='number of policy updates (default: 10000)')
parser.add_argument('--eta', type=float, default=0,
                    help='η parameter for EWF, Exp3, Exp3P')
parser.add_argument('--gamma', type=float, default=0,
                    help='γ parameter for Exp3P')
parser.add_argument('--beta', type=float, default=0,
                    help='β parameter for Exp3P')
parser.add_argument('--nb-seeds', type=int, default=5,
                    help='number of seeds to average the results on (default: 5)')
args = parser.parse_args()

assert args.game in ['NFG', 'TTT']
assert args.algo in ['EWF', 'Exp3', 'Exp3P', 'CFR']

if args.algo in ['EWF', 'Exp3']:
    hyper_params = 'η{}'.format(args.eta)
elif args.algo == 'Exp3P':
    hyper_params = 'η{}_γ{}_β{}'.format(args.eta, args.gamma, args.beta)
elif args.algo == 'CFR':
    hyper_params = ''
writer_path = 'storage/{}_{}_N{}_{}'.format(args.game, args.algo, args.iters, hyper_params)

# For plots
matplotlib.rcParams.update({'font.size': 8})
os.makedirs(writer_path, exist_ok=True)

iters = np.arange(1, args.iters+1)

if args.game == 'NFG':
    game = NormalFormGame()

    if args.algo in ['EWF', 'Exp3', 'Exp3P']:
        actions = game.init_h.I.available_actions

        # For plots
        N_KLss_0 = []
        N_KLss_1 = []
        E_gainss_0 = []
        E_gainss_1 = []
        regretss_0 = []
        regretss_1 = []

        for seed in tqdm(range(args.nb_seeds)):
            np.random.seed(seed)

            p0 = load_MAB_algo(actions, args)
            p1 = load_MAB_algo(actions, args)

            # For plots
            N_KLs_0 = []
            N_KLs_1 = []
            E_gains_0 = []
            E_gains_1 = []
            regrets_0 = []
            regrets_1 = []
            S0 = {a: 0 for a in actions}
            S1 = {a: 0 for a in actions}

            for i in tqdm(iters):
                a0 = p0.play()
                a1 = p1.play()
                h = game.init_h.next(a0).next(a1)
                if args.algo in ['Exp3', 'Exp3P']:
                    u0_a = game.u(h, 0)
                    u1_a = -u0_a
                    p0.update_policy(u0_a)
                    p1.update_policy(u1_a)
                elif args.algo == 'EWF':
                    u0 = game._u0_matrix[:, a1]
                    u1 = -game._u0_matrix[a0]
                    p0.update_policy(u0)
                    p1.update_policy(u1)

                # For plots
                π0 = p0.π
                π1 = p1.π
                E_gain_0, E_gain_1 = compute_NFG_expected_gains(π0, π1)
                E_gains_0.append(E_gain_0)
                E_gains_1.append(E_gain_1)
                KL_0 = compute_NFG_KL(0, π0)
                KL_1 = compute_NFG_KL(1, π1)
                N_KLs_0.append(KL_0)
                N_KLs_1.append(KL_1)
                u0, u1 = compute_NFG_players_utility(a0, a1)
                S0 = {a: S0[a] + u0[a] - u0[a0] for a in actions}
                S1 = {a: S1[a] + u1[a] - u1[a1] for a in actions}
                regret_0 = 1/i * max([S0[a] for a in actions])
                regret_1 = 1/i * max([S1[a] for a in actions])
                regrets_0.append(regret_0)
                regrets_1.append(regret_1)

            # For plots
            N_KLss_0.append(N_KLs_0)
            N_KLss_1.append(N_KLs_1)
            E_gainss_0.append(E_gains_0)
            E_gainss_1.append(E_gains_1)
            regretss_0.append(regrets_0)
            regretss_1.append(regrets_1)

        # For plots
        plt.subplot(3, 2, 1)
        plt.plot(iters, smooth(np.mean(N_KLss_0, axis=0)))
        plt.ylim(0, .5)
        plt.title("KL with NE 1")
        plt.subplot(3, 2, 2)
        plt.plot(iters, smooth(np.mean(N_KLss_1, axis=0)))
        plt.ylim(0, .5)
        plt.title("KL with NE 2")
        plt.subplot(3, 2, 3)
        plt.plot(iters, smooth(np.mean(E_gainss_0, axis=0)))
        plt.axhline(y=NormalFormGame.v0, color='r')
        plt.title("Expected gain & value 1")
        plt.subplot(3, 2, 4)
        plt.plot(iters, smooth(np.mean(E_gainss_1, axis=0)))
        plt.axhline(y=NormalFormGame.v1, color='r')
        plt.title("Expected gain & value 2")
        plt.subplot(3, 2, 5)
        plt.plot(iters, smooth(np.mean(regretss_0, axis=0)))
        plt.ylim(0, 1)
        plt.title("Regret 1")
        plt.subplot(3, 2, 6)
        plt.plot(iters, smooth(np.mean(regretss_1, axis=0)))
        plt.ylim(0, 1)
        plt.title("Regret 2")
        plt.tight_layout()
        plt.savefig(writer_path + "/plots")

    elif args.algo == 'CFR':
        # For plots
        N_KLss_0 = []
        N_KLss_1 = []
        regretss_0 = []
        regretss_1 = []

        for seed in tqdm(range(args.nb_seeds)):
            np.random.seed(seed)

            cfr = CFR(game)

            # For plots
            N_KLs_0 = []
            N_KLs_1 = []
            regrets_0 = []
            regrets_1 = []

            for i in tqdm(iters):
                cfr.update_policy()

                # For plots
                π0 = cfr.aσ[0]
                π1 = cfr.aσ[1]
                KL_0 = compute_NFG_KL(0, π0)
                KL_1 = compute_NFG_KL(1, π1)
                N_KLs_0.append(KL_0)
                N_KLs_1.append(KL_1)
                regret_0 = 1/cfr.T*max(cfr.S[0].values())
                regret_1 = 1/cfr.T*max(cfr.S[1].values())
                regrets_0.append(regret_0)
                regrets_1.append(regret_1)

            # For plots
            N_KLss_0.append(N_KLs_0)
            N_KLss_1.append(N_KLs_1)
            regretss_0.append(regrets_0)
            regretss_1.append(regrets_1)

        # For plots
        plt.subplot(2, 2, 1)
        plt.plot(iters, smooth(np.mean(N_KLss_0, axis=0)))
        plt.ylim(0, .5)
        plt.title("KL with NE 1")
        plt.subplot(2, 2, 2)
        plt.plot(iters, smooth(np.mean(N_KLss_1, axis=0)))
        plt.ylim(0, .5)
        plt.title("KL with NE 2")
        plt.subplot(2, 2, 3)
        plt.plot(iters, smooth(np.mean(regretss_0, axis=0)))
        plt.ylim(0, 1)
        plt.title("Regret 1")
        plt.subplot(2, 2, 4)
        plt.plot(iters, smooth(np.mean(regretss_1, axis=0)))
        plt.ylim(0, 1)
        plt.title("Regret 2")
        plt.tight_layout()
        plt.savefig(writer_path + "/plots")