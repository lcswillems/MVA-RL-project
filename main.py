import argparse
import datetime
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np
import os

from algos import CFR
from games import mRPS, TTT
from utils import hps_to_tstr, hps_to_fstr, load_MAB_algo, plot, compute_mRPS_KL,\
                  compute_mRPS_expected_gains, compute_mRPS_players_utility

parser = argparse.ArgumentParser()
parser.add_argument('--game', required=True,
                    help='game: mRPS or TTT')
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

assert args.game in ['mRPS', 'TTT']
assert args.algo in ['EWF', 'Exp3', 'Exp3P', 'CFR', 'CFRp']

is_MAB_algo = args.algo in ['EWF', 'Exp3', 'Exp3P']
is_CFR_algo = args.algo in ['CFR', 'CFRp']

if args.algo in ['EWF', 'Exp3']:
    hps = {'η': args.eta}
elif args.algo == 'Exp3P':
    hps = {'η': args.eta, 'γ': args.gamma, 'β': args.beta}
elif args.algo in ['CFR', 'CFRp']:
    hps = {}
writer_path = 'storage/{}_{}_N{}_{}'.format(args.game, args.algo, args.iters, hps_to_fstr(hps))

# For plots
matplotlib.rcParams.update({'font.size': 8})
os.makedirs(writer_path, exist_ok=True)

iters = np.arange(1, args.iters+1)

if args.game == 'mRPS':
    game = mRPS()
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

        if is_MAB_algo:
            algo0 = load_MAB_algo(actions, args)
            algo1 = load_MAB_algo(actions, args)
        elif is_CFR_algo:
            algo = CFR(game)

        # For plots
        N_KLs_0 = []
        N_KLs_1 = []
        E_gains_0 = []
        E_gains_1 = []
        if is_MAB_algo:
            S0 = {a: 0 for a in actions}
            S1 = {a: 0 for a in actions}
        regrets_0 = []
        regrets_1 = []

        for i in tqdm(iters):
            if is_MAB_algo:
                a0 = algo0.play()
                a1 = algo1.play()
                h = game.init_h.next(a0).next(a1)
                if args.algo in ['Exp3', 'Exp3P']:
                    u0_a = game.u(h, 0)
                    u1_a = -u0_a
                    algo0.update_policy(u0_a)
                    algo1.update_policy(u1_a)
                elif args.algo == 'EWF':
                    u0 = game._u0_matrix[:, a1]
                    u1 = -game._u0_matrix[a0]
                    algo0.update_policy(u0)
                    algo1.update_policy(u1)

                # For plots
                σ0 = algo0.aσi
                σ1 = algo1.aσi
            elif is_CFR_algo:
                algo.update_policy()

                # For plots
                σ0 = algo.aσ[0]
                σ1 = algo.aσ[1]

            # For plots
            E_gain_0, E_gain_1 = compute_mRPS_expected_gains(σ0, σ1)
            E_gains_0.append(E_gain_0)
            E_gains_1.append(E_gain_1)
            KL_0 = compute_mRPS_KL(0, σ0)
            KL_1 = compute_mRPS_KL(1, σ1)
            N_KLs_0.append(KL_0)
            N_KLs_1.append(KL_1)
            if is_MAB_algo:
                u0, u1 = compute_mRPS_players_utility(a0, a1)
                S0 = {a: S0[a] + u0[a] - u0[a0] for a in actions}
                S1 = {a: S1[a] + u1[a] - u1[a1] for a in actions}
                regret_0 = 1/i * max([S0[a] for a in actions])
                regret_1 = 1/i * max([S1[a] for a in actions])
            elif is_CFR_algo:
                regret_0 = 1/algo.T*max(algo.S[0].values())
                regret_1 = 1/algo.T*max(algo.S[1].values())
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
    plt.suptitle("{} {}".format(args.algo, hps_to_tstr(hps)), size=12, weight='bold')
    plt.subplot(3, 2, 1)
    plot(plt, iters, N_KLss_0)
    plt.ylim(0, .5)
    plt.title("KL with NE 1")
    plt.subplot(3, 2, 2)
    plot(plt, iters, N_KLss_1)
    plt.ylim(0, .5)
    plt.title("KL with NE 2")
    plt.subplot(3, 2, 3)
    plot(plt, iters, E_gainss_0)
    plt.axhline(y=mRPS.v0, color='r')
    plt.ylim(.1, .6)
    plt.title("Expected gain & value 1")
    plt.subplot(3, 2, 4)
    plot(plt, iters, E_gainss_1)
    plt.axhline(y=mRPS.v1, color='r')
    plt.ylim(-.6, -.1)
    plt.title("Expected gain & value 2")
    plt.subplot(3, 2, 5)
    plot(plt, iters, regretss_0)
    plt.ylim(0, 1)
    plt.title("Regret 1")
    plt.subplot(3, 2, 6)
    plot(plt, iters, regretss_1)
    plt.ylim(0, 1)
    plt.title("Regret 2")
    plt.tight_layout(rect=[0, 0, 1, .95])
    plt.savefig(writer_path + "/plots")