import copy
from functools import lru_cache

from .generic import History, InformationSet

class TTTHistory(History):
    def __init__(self, h=None, a=None):
        self._player = 0 if h == None else (h.player + 1) % 2

        super().__init__(h, a)

    @property
    def player(self):
        return self._player

    @property
    def _information_set_class(self):
        return TTTInformationSet

class TTTInformationSet(InformationSet):
    def __init__(self, h):
        super().__init__(h)

        if h == None:
            self.grid = [[0 for _ in range(3)] for _ in range(3)]
            self._free_actions = list(range(9))
        else:
            prev_h, prev_a = h.previous
            self.grid = [[item for item in line] for line in prev_h.I.grid]
            self._free_actions = [item for item in prev_h.I._free_actions]
            self._add_grid(prev_a, prev_h.player)

        self._id = 2*sum([self._get_grid(i)*3**i for i in range(9)]) + self.player

    def _get_grid(self, id):
        return self.grid[id//3][id%3]

    def _add_grid(self, id, player):
        self.grid[id//3][id%3] = player+1
        self._free_actions.remove(id)

    @property
    def id(self):
        return self._id

    @property
    def available_actions(self):
        if not self.terminal:
            return self._free_actions
        return []

    @property
    def initial(self):
        return len(self._free_actions) == 9

    @property
    def terminal(self):
        return len(self._free_actions) == 0 or self.winner is not None

    @property
    @lru_cache()
    def winner(self):
        for i in range(3):
            # Lines
            if self.grid[i][0] != 0 and self.grid[i][0] == self.grid[i][1] == self.grid[i][2]:
                return self.grid[i][0]
            # Columns
            if self.grid[0][i] != 0 and self.grid[0][i] == self.grid[1][i] == self.grid[2][i]:
                return self.grid[0][i]
        # Diagonal 1
        if self.grid[0][0] != 0 and self.grid[0][0] == self.grid[1][1] == self.grid[2][2]:
            return self.grid[0][0]
        # Diagonal 2
        if self.grid[0][2] != 0 and self.grid[0][2] == self.grid[1][1] == self.grid[2][0]:
            return self.grid[0][2]
        return None

class TicTacToe:
    def __init__(self):
        self.nb_players = 2
        self.init_h = TTTHistory()

    def u(self, h, player):
        if player == h.I.winner:
            return 1
        return -1