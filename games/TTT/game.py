import copy

class TTTHistory:
    def __init__(self, h=None, a=None):
        if h == None and a == None:
            self.sequence = []
            self.previous = None
            self.I = TTTInformationSet()
        else:
            self.sequence = h.sequence + [a]
            self.previous = (h, a)
            self.I = TTTInformationSet(h, a)
        self.player = self.I.player
        self.nexts = {}
        self._id = self.sequence

    def next(self, a):
        if a not in self.nexts:
            self.nexts[a] = TTTHistory(self, a)
        return self.nexts[a]

    def __str__(self):
        return str(self.sequence)

    def __repr__(self):
        return self.__str__()

class TTTInformationSet:
    def __init__(self, h=None, a=None):
        if h == None and a == None:
            self.grid = [[0 for _ in range(3)] for _ in range(3)]
            self.free_ids = list(range(9))
            self.player = 0
        else:
            assert a in h.I.available_actions
            self.grid = [[item for item in line] for line in h.I.grid]
            self.free_ids = [item for item in h.I.free_ids]
            self._add_grid(a, h.player)
            self.player = (h.player + 1) % 2
        self._id = 2*sum([self._get_grid(i)*3**i for i in range(9)]) + self.player

    def _get_grid(self, id):
        return self.grid[id//3][id%3]

    def _add_grid(self, id, player):
        self.grid[id//3][id%3] = player+1
        self.free_ids.remove(id)

    def __eq__(self, other):
        return self._id == other._id

    def __hash__(self):
        return self._id

    @property
    def available_actions(self):
        if not self.terminal:
            return self.free_ids
        return []

    def _compute_winner(self):
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

    @property
    def winner(self):
        if not hasattr(self, "_winner"):
            self._winner = self._compute_winner()
        return self._winner

    @property
    def initial(self):
        return len(self.free_ids) == 9

    @property
    def terminal(self):
        if not hasattr(self, "_terminal"):
            self._terminal = len(self.free_ids) == 0 or self.winner is not None
        return self._terminal

    def u(self, player):
        assert player in [0, 1]
        if player == self.winner:
            return 1
        return -1

class TicTacToe:
    nb_players = 2
    initial_history = TTTHistory()

    def cache_tree(self):
        stack = [self.initial_history]
        self.Is = set()
        self.hTs = []

        while len(stack) != 0:
            h = stack.pop()
            self.Is.add(h.I)
            if h.I.terminal:
                self.hTs.append(h)
            for a in h.I.available_actions:
                next_h = h.next(a)
                stack.append(next_h)