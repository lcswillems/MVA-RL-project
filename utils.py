import scipy.stats as stats
import numpy as np

def compute_normalized_entropy(π):
    d = list(π.values())
    return stats.entropy(d) / np.log(len(d))

RPS_u0_matrix = [
    [0, -1, 1],
    [1, 0, -1],
    [-1, 1, 0]
]

def compute_RPS_players_utility(a0, a1):
    u0 = {}
    u1 = {}
    for a in range(3):
        u0[a] = RPS_u0_matrix[a][a1]
        u1[a] = -RPS_u0_matrix[a0][a]
    return u0, u1

def compute_RPS_expected_gains(π0, π1):
    E_gain_0 = 0
    for a0 in range(3):
        for a1 in range(3):
            E_gain_0 += π0[a0]*π1[a1]*RPS_u0_matrix[a0][a1]
    return E_gain_0, -E_gain_0