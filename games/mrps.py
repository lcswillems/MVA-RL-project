import numpy as np

from .generic import ZeroSumNormalFormGameHistory, ZeroSumNormalFormGameInformationSet

class mRPSHistory(ZeroSumNormalFormGameHistory):
    @property
    def _information_set_class(self):
        return mRPSInformationSet

class mRPSInformationSet(ZeroSumNormalFormGameInformationSet):
    @property
    def available_actions(self):
        if self.id < 2:
            return [0, 1, 2]
        return []

class mRPS:
    """Modified Rock Paper Scissors game."""

    _u0_matrix = np.array([
        [0, -1, 5],
        [1, 0, -1],
        [-1, 1, 0]
    ])
    σ0 = np.array([1/7, 11/21, 1/3])
    v0 = 4/21
    σ1 = np.array([1/3, 11/21, 1/7])
    v1 = -4/21

    def __init__(self):
        self.nb_players = 2
        self.init_h = mRPSHistory()

    def u(self, h, player):
        u0 = self._u0_matrix[h.sequence[0]][h.sequence[1]]
        return [u0, -u0][player]