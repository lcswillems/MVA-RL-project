import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

from algos import EWF, Exp3, Exp3P, CFR, CFRp

def hps_to_fstr(hps):
    return '_'.join(['{}{}'.format(hp, v) for hp, v in hps.items()])

def hps_to_tstr(hps):
    return ' '.join(['{}={}'.format(hp, v) for hp, v in hps.items()])

def load_MAB_algo(actions, args):
    if args.algo == 'EWF':
        return EWF(actions, args.eta)
    elif args.algo == 'Exp3':
        return Exp3(actions, args.eta)
    elif args.algo == 'Exp3P':
        return Exp3P(actions, args.eta, args.gamma, args.beta)

def load_CFR_algo(game, args):
    if args.algo == 'CFR':
        return CFR(game)
    elif args.algo == 'CFRp':
        return CFRp(game)

def plot(plt, iters, valuess):
    m = np.amin(valuess, axis=0)
    median = np.median(valuess, axis=0)
    M = np.amax(valuess, axis=0)
    plt.plot(iters, median)
    plt.fill_between(iters, m, M, alpha=.3)

def compute_dist_dist(game, player, σi):
    σi = np.array(list(σi.values()))
    ne_σi = getattr(game, 'σ{}'.format(player))
    return np.linalg.norm(σi - ne_σi, ord=1)

def compute_players_utility(game, a0, a1):
    u0 = {}
    u1 = {}
    for a in range(3):
        u0[a] = game._u0_matrix[a][a1]
        u1[a] = -game._u0_matrix[a0][a]
    return u0, u1

def compute_expected_gains(game, σ0, σ1):
    E_gain_0 = 0
    for a0 in range(3):
        for a1 in range(3):
            E_gain_0 += σ0[a0]*σ1[a1]*game._u0_matrix[a0][a1]
    return E_gain_0, -E_gain_0