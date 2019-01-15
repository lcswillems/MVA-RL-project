from abc import ABC, abstractproperty, abstractmethod

class History:
    def __init__(self, h=None, a=None):
        self.previous = (h, a)
        self.sequence = [] if h == None else h.sequence + [a]
        self.nexts = {}

        self.I = self._information_set_class(self)

    @abstractproperty
    def player(self):
        pass

    @abstractproperty
    def _information_set_class(self):
        pass

    def next(self, a):
        assert a in self.I.available_actions
        if a not in self.nexts:
            self.nexts[a] = self.__class__(self, a)
        return self.nexts[a]

    def __str__(self):
        return str(self.sequence)

    def __repr__(self):
        return self.__str__()

class InformationSet:
    def __init__(self, h):
        self.player = h.player

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return self.__str__()

    @abstractproperty
    def id(self):
        pass

    @abstractproperty
    def available_actions(self):
        pass

    @abstractproperty
    def initial(self):
        pass

    @abstractproperty
    def terminal(self):
        pass