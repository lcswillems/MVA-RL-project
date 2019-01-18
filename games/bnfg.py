import numpy as np

from .generic import ZeroSumNormalFormGameHistory, ZeroSumNormalFormGameInformationSet

class bNFGHistory(ZeroSumNormalFormGameHistory):
    @property
    def _information_set_class(self):
        return bNFGInformationSet

class bNFGInformationSet(ZeroSumNormalFormGameInformationSet):
    @property
    def available_actions(self):
        if self.id < 2:
            return list(range(15))
        return []

class bNFG:
    """Big Normal Form Game."""

    _u0_matrix = np.array([
        [-3, -3, 1, -3, 2, 3, -3, 0, 1, 1, -1, -3, 2, -2, 3],
        [-3, 3, 1, -1, 2, 0, -1, 2, 2, 3, -2, -3, 0, 3, -3],
        [0, -3, 3, 3, 3, -1, 2, -1, 2, -2, 2, 0, 1, 1, 2],
        [1, -1, -3, 2, -3, -2, 1, 2, 3, 0, -2, -1, 2, -1, 0],
        [-2, -1, 3, -1, 1, -1, 3, 0, 0, -1, 3, -3, -1, 3, -3],
        [1, -3, -1, 0, -1, 0, 0, 2, 3, -1, -1, 2, 2, 3, -2],
        [2, 0, 2, 2, 3, -2, 1, -2, -2, 0, -1, -1, -3, 2, 1],
        [0, 3, -1, -3, 2, 3, 1, -2, -3, 0, -2, -1, -1, -2, -1],
        [-3, 2, 2, -1, -2, -1, 0, 2, -2, 1, 3, -1, 0, -1, 1],
        [-1, -3, 2, -1, 3, 3, 3, -3, -3, -3, 0, -1, 3, -3, 1],
        [-2, -2, 2, 2, 2, 0, -1, 1, 0, -1, -1, -3, -2, 2, 2],
        [-3, 0, 3, 2, 2, -1, 0, 2, -1, 0, 1, -1, -3, -3, -2],
        [-3, 2, -1, 0, -1, 0, -3, 3, 1, -1, 0, 2, 2, 3, -3],
        [2, 3, 0, -1, -3, -1, -3, -2, 3, 0, 0, 0, 1, 0, -1],
        [3, 0, -3, -3, -1, -1, -2, 1, 2, -3, 1, 3, -1, 2, -2]
    ])
    σ0 = np.array([693/13219, 194/13219, 862/13219, 0, 0, 3396/13219, 2956/13219, 1820/13219, 2464/13219, 0, 0, 0, 576/13219, 258/13219, 0])
    v0 = -1957/13219
    σ1 = np.array([28169/978206, 24761/489103, 0, 72021/489103, 0, 86134/489103, 0, 0, 11169/489103, 260987/978206, 5084/489103, 95143/489103, 0, 0, 50213/489103])
    v1 = 1957/13219

    def __init__(self):
        self.nb_players = 2
        self.init_h = bNFGHistory()

    def u(self, h, player):
        u0 = self._u0_matrix[h.sequence[0]][h.sequence[1]]
        return [u0, -u0][player]