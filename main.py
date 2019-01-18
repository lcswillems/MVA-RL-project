import argparse
import datetime
import matplotlib
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np

from algos import TTT_expert_σ
from games import mRPS, bNFG, TTT
from utils import hps_to_tstr, hps_to_fstr, load_MAB_algo, load_CFR_algo, plot, compute_dist_dist,\
                  compute_expected_gains, compute_players_utility

parser = argparse.ArgumentParser()
parser.add_argument('--game', required=True,
                    help='game: mRPS, bNFG or TTT')
parser.add_argument('--algo', required=True,
                    help='algorithm: Exp3P or CFR')
parser.add_argument('--iters', type=int, default=10000,
                    help='number of policy updates (default: 10000)')
parser.add_argument('--eval-iters', type=int, default=1000,
                    help='number of parties again expert to evaluate (default: 1000)')
parser.add_argument('--eta', type=float, default=0,
                    help='η parameter for EWF, Exp3, Exp3P')
parser.add_argument('--gamma', type=float, default=0,
                    help='γ parameter for Exp3P')
parser.add_argument('--beta', type=float, default=0,
                    help='β parameter for Exp3P')
parser.add_argument('--nb-seeds', type=int, default=5,
                    help='number of seeds to average the results on for MAB algos (default: 5)')
args = parser.parse_args()

assert args.game in ['mRPS', 'bNFG', 'TTT']
assert args.algo in ['EWF', 'Exp3', 'Exp3P', 'CFR', 'CFRp']

is_MAB_algo = args.algo in ['EWF', 'Exp3', 'Exp3P']
is_CFR_algo = args.algo in ['CFR', 'CFRp']

if args.algo in ['EWF', 'Exp3']:
    hps = {'η': args.eta}
elif args.algo == 'Exp3P':
    hps = {'η': args.eta, 'γ': args.gamma, 'β': args.beta}
elif args.algo in ['CFR', 'CFRp']:
    hps = {}

# For plots
matplotlib.rcParams.update({'font.size': 8})

iters = np.arange(1, args.iters+1)

if args.game in ['mRPS', 'bNFG']:
    if args.game == 'mRPS':
        game = mRPS()
    elif args.game == 'bNFG':
        game = bNFG()
    actions = game.init_h.I.available_actions

    # For plots
    N_distss_0 = []
    N_distss_1 = []
    E_gainss_0 = []
    E_gainss_1 = []
    regretss_0 = []
    regretss_1 = []

    for i, seed in tqdm(enumerate(range(args.nb_seeds))):
        if is_CFR_algo and i > 0:
            break

        np.random.seed(seed)

        if is_MAB_algo:
            algo0 = load_MAB_algo(actions, args)
            algo1 = load_MAB_algo(actions, args)
        elif is_CFR_algo:
            algo = load_CFR_algo(game, args)

        # For plots
        N_dists_0 = []
        N_dists_1 = []
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
            E_gain_0, E_gain_1 = compute_expected_gains(game, σ0, σ1)
            E_gains_0.append(E_gain_0)
            E_gains_1.append(E_gain_1)
            dist_0 = compute_dist_dist(game, 0, σ0)
            dist_1 = compute_dist_dist(game, 1, σ1)
            N_dists_0.append(dist_0)
            N_dists_1.append(dist_1)
            if is_MAB_algo:
                u0, u1 = compute_players_utility(game, a0, a1)
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
        N_distss_0.append(N_dists_0)
        N_distss_1.append(N_dists_1)
        E_gainss_0.append(E_gains_0)
        E_gainss_1.append(E_gains_1)
        regretss_0.append(regrets_0)
        regretss_1.append(regrets_1)

    # For plots
    plot_path = 'storage/{}_{}_N{}_{}.png'.format(args.game, args.algo, args.iters, hps_to_fstr(hps))
    plt.suptitle("{} {}".format(args.algo, hps_to_tstr(hps)), size=12, weight='bold')
    plt.subplot(3, 2, 1)
    plot(plt, iters, N_distss_0)
    plt.ylim(0, .5)
    plt.title("Distance to NE 1")
    plt.subplot(3, 2, 2)
    plot(plt, iters, N_distss_1)
    plt.ylim(0, .5)
    plt.title("Distance to NE 2")
    plt.subplot(3, 2, 3)
    plot(plt, iters, E_gainss_0)
    plt.axhline(y=game.v0, color='r')
    plt.ylim(0, .5)
    plt.title("Expected utility & value 1")
    plt.subplot(3, 2, 4)
    plot(plt, iters, E_gainss_1)
    plt.axhline(y=game.v1, color='r')
    plt.ylim(-.5, 0)
    plt.title("Expected utility & value 2")
    plt.subplot(3, 2, 5)
    plot(plt, iters, regretss_0)
    plt.ylim(0, 1)
    plt.title("Regret 1")
    plt.subplot(3, 2, 6)
    plot(plt, iters, regretss_1)
    plt.ylim(0, 1)
    plt.title("Regret 2")
    plt.tight_layout(rect=[0, 0, 1, .95])
    plt.savefig(plot_path)

elif args.game == 'TTT':
    assert args.algo in ['CFR', 'CFRp']

    eval_iters = np.arange(1, args.eval_iters+1)

    game = TTT()
    algo = load_CFR_algo(game, args)
    expert_σ = TTT_expert_σ(game)

    # For plots
    mean_us = []

    for _ in tqdm(iters):
        algo.update_policy()

        us = []
        for i in tqdm(eval_iters):
            h = game.init_h
            j0 = i%2
            j = 0
            while not h.I.terminal:
                if j == j0:
                    d = algo.σ[h.I.id]
                    a = np.random.choice(list(d.keys()), p=list(d.values()))
                else:
                    a = expert_σ[h.I.id]
                h = h.next(a)
                j = (j+1)%2
            us.append(game.u(h, j0))

        # For plots
        mean_us.append(np.mean(us))

    # For plots
    plot_path = 'storage/{}_{}_N{}.png'.format(args.game, args.algo, args.iters)
    plt.suptitle(args.algo, size=12, weight='bold')
    plt.plot(iters, mean_us)
    plt.ylim(-1.1, 0.1)
    plt.title("Average utility")
    plt.tight_layout(rect=[0, 0, 1, .95])
    plt.savefig(plot_path)