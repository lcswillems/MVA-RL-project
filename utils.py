import scipy.stats as stats
import numpy as np
from games import NormalFormGame

def compute_NFG_KL(player, π):
    π = list(π.values())
    ne_π = getattr(NormalFormGame, 'π{}'.format(player))
    return stats.entropy(π, ne_π)

def compute_NFG_players_utility(a0, a1):
    u0 = {}
    u1 = {}
    for a in range(3):
        u0[a] = NormalFormGame._u0_matrix[a][a1]
        u1[a] = -NormalFormGame._u0_matrix[a0][a]
    return u0, u1

def compute_NFG_expected_gains(π0, π1):
    E_gain_0 = 0
    for a0 in range(3):
        for a1 in range(3):
            E_gain_0 += π0[a0]*π1[a1]*NormalFormGame._u0_matrix[a0][a1]
    return E_gain_0, -E_gain_0