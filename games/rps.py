from .generic import History, InformationSet

class RPSHistory(History):
    def __init__(self, h=None, a=None):
        self._player = 0 if h == None else h.player + 1

        super().__init__(h, a)

    @property
    def player(self):
        return self._player

    @property
    def _information_set_class(self):
        return RPSInformationSet

class RPSInformationSet(InformationSet):
    def __init__(self, h):
        super().__init__(h)

    @property
    def id(self):
        return self.player

    @property
    def available_actions(self):
        if self.id < 2:
            return [0, 1, 2]
        return []

    @property
    def initial(self):
        return self.id == 0

    @property
    def terminal(self):
        return self.id == 2

class RockPaperScissors:
    def __init__(self):
        self.nb_players = 2
        self.init_h = RPSHistory()
        self._u_matrix = [
            [0, -1, 1],
            [1, 0, -1],
            [-1, 1, 0]
        ]

    def u(self, h, player):
        u1 = self._u_matrix[h.sequence[0]][h.sequence[1]]
        return [u1, -u1][player]