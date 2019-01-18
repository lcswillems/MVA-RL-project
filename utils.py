import scipy.stats as stats
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

from algos import EWF, Exp3, Exp3P, CFR
from games import mRPS

def load_MAB_algo(actions, args):
    if args.algo == 'EWF':
        return EWF(actions, args.eta)
    elif args.algo == 'Exp3':
        return Exp3(actions, args.eta)
    elif args.algo == 'Exp3P':
        return Exp3P(actions, args.eta, args.gamma, args.beta)

def plot(plt, iters, valuess, σ=5):
    m = np.amin(valuess, axis=0)
    median = np.median(valuess, axis=0)
    M = np.amax(valuess, axis=0)
    plt.plot(iters, median)
    plt.fill_between(iters, m, M, alpha=.3)

def compute_mRPS_KL(player, σi):
    σi = list(σi.values())
    ne_σi = getattr(mRPS, 'σ{}'.format(player))
    return stats.entropy(σi, ne_σi)

def compute_mRPS_players_utility(a0, a1):
    u0 = {}
    u1 = {}
    for a in range(3):
        u0[a] = mRPS._u0_matrix[a][a1]
        u1[a] = -mRPS._u0_matrix[a0][a]
    return u0, u1

def compute_mRPS_expected_gains(σ0, σ1):
    E_gain_0 = 0
    for a0 in range(3):
        for a1 in range(3):
            E_gain_0 += σ0[a0]*σ1[a1]*mRPS._u0_matrix[a0][a1]
    return E_gain_0, -E_gain_0