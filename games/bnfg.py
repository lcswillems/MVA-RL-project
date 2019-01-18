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

    _u0_matrix = np.array([[1, 3, 3, -3, 2, 3, -2, 2, 1, -2, 0, 3, -3, 2, 1], [1, 2, -2, -3, -1, 1, -1, 1, 0, 3, 1, 2, 1, 2, 0], [2, -3, 0, 0, -3, 3, -3, 2, 2, 1, 2, 1, 1, 3, -1], [1, -1, -3, -2, -1, -3, 2, 1, -2, 3, 3, 2, -3, 2, 1], [-2, 2, -2, 1, -3, 2, 3, 3, 1, 0, 2, 0, 1, 0, 1], [1, 0, -2, 2, 3, 1, -3, -1, 0, 1, -2, -1, -3, 1, -1], [3, 1, -2, 0, -2, -3, 3, 1, -3, -2, -3, -1, -3, 2, 1], [-3, 2, 0, 3, 0, -1, 1, 3, -2, -2, 0, -2, -1, 2, 2], [2, -1, 3, 2, -3, 3, -1, -3, -2, -3, 2, 3, 0, 1, 2], [2, -3, 2, 0, 2, 0, -1, 1, -1, 2, -3, 3, 2, 3, 2], [2, -3, -2, 2, 2, 2, 0, -3, 2, 0, 2, -3, -2, -1, -2], [-1, -1, 0, 3, -1, 0, -1, -3, 0, -1, 3, 0, 0, -2, -2], [-3, -3, -1, -3, 1, -1, -2, -1, 0, 3, -1, 2, 1, 1, 3], [0, 0, 2, -3, 3, -2, 1, 0, 2, 0, -1, -1, -1, 1, -2], [-2, -2, 3, -3, -3, -3, 1, 2, -1, -1, 2, 2, -2, 3, 2]])
    σ0 = np.array([23773/157153, 12853/157153, 0, 0, 40169/157153, 0, 0, 12837/157153, 0, 42261/157153, 14791/157153, 9272/157153, 0, 1197/157153, 0])
    v0 = 22609/157153
    σ1 = np.array([17428/157153, 25749/157153, 5663/157153, 362/3833, 32672/157153, 0, 9296/157153, 0, 0, 0, 21076/157153, 0, 30427/157153, 0, 0])
    v1 = -22609/157153

    def __init__(self):
        self.nb_players = 2
        self.init_h = bNFGHistory()

    def u(self, h, player):
        u0 = self._u0_matrix[h.sequence[0]][h.sequence[1]]
        return [u0, -u0][player]