import numpy as np

# All the notations are taken from: http://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf.
# The code only works for perfect recall games.

class CFR:
    """CFR algorithm."""

    def __init__(self, G):
        self.G = G
        self._cache_tree_game()

        self.T = 0
        self._init_Sp()
        self._init_σ_aσ()

    def _cache_tree_game(self):
        print("Caching game tree...")

        self.G.player_uIs = {}
        self.G.hTs = []

        stack = [self.G.init_h]
        while len(stack) != 0:
            h = stack.pop()
            if h.I.terminal:
                self.G.hTs.append(h)
            else:
                if not h.I.player in self.G.player_uIs.keys():
                    self.G.player_uIs[h.I.player] = set()
                self.G.player_uIs[h.I.player].add(h.I)
            for a in h.I.available_actions:
                next_h = h.next(a)
                stack.append(next_h)

        self.G.uIs = set.union(*self.G.player_uIs.values())

        print("Game tree cached.")

    def _init_Sp(self):
        # S[I.id][a] gives T*R_i^{T}(I, a) where i = I.player and T = self.T.
        self.S = {}
        # Sp[I.id][a] gives T*R_i^{T+}(I, a) where i = I.player and T = self.T.
        self.Sp = {}
        for I in self.G.uIs:
            self.S[I.id] = {a: 0 for a in I.available_actions}
            self.Sp[I.id] = {a: 0 for a in I.available_actions}

    def _init_σ_aσ(self):
        # σ[I.id][a] gives σ_i(I)(a) where i = I.player.
        self.σ = {}
        self.sσ_num = {}
        self.sσ_den = {}
        # σa[I.id][a] gives the average σ_i(I)(a) where i = I.player.
        self.aσ = {}
        for I in self.G.uIs:
            l = len(I.available_actions)
            self.σ[I.id] = {a: 1/l for a in I.available_actions}
            self.sσ_num[I.id] = {a: 0 for a in I.available_actions}
            self.sσ_den[I.id] = {a: 0 for a in I.available_actions}
            self.aσ[I.id] = {a: self.σ[I.id][a] for a in I.available_actions}

    def update_policy(self):
        self.T += 1
        if not hasattr(self, 'uIs'):
            self.running_uIs = self.G.uIs
        self._compute_v()
        self._update_Sp()
        self._update_σ()
        self._update_aσ()

    def _compute_v(self):
        # v[I.id] gives u'_i(σ, I) where i = I.player.
        # v[I.id, a] gives u'_i(σ|I->a, I) where i = I.player.
        self.v = {}

        # π_[i, h] gives π^σ_{-i}(h).
        self.π_ = {}

        # π[I.id] gives π^σ(I).
        # π[h, hT] gives π^σ(h, hT).
        self.π = {}

        for I in self.G.uIs:
            self.v[I.id] = 0
            self.π[I.id] = 0
            for a in I.available_actions:
                self.v[I.id, a] = 0

        h = self.G.init_h
        self.π[h.I.id] += 1
        for i2 in range(self.G.nb_players):
            self.π_[i2, h] = 1
        stack = [h]
        while len(stack) != 0:
            h = stack.pop()
            i = h.player
            for a in h.I.available_actions:
                next_h = h.next(a)
                stack.append(next_h)
                for i2 in range(self.G.nb_players):
                    if not next_h.I.terminal:
                        self.π[next_h.I.id] += self.π[h.I.id] * self.σ[h.I.id][a]
                    p = 1 if i == i2 else self.σ[h.I.id][a]
                    self.π_[i2, next_h] = self.π_[i2, h] * p

        for hT in self.G.hTs:
            self.π[hT, hT] = 1
            h = hT

            while not h.I.initial:
                next_h = h
                h, a = next_h.previous

                self.π[h, hT] = self.σ[h.I.id][a] * self.π[next_h, hT]

                self.v[h.I.id] += self.π_[h.player, h] * self.π[h, hT] * self.G.u(hT, h.I.player)
                self.v[h.I.id, a] += self.π_[h.player, h] * self.π[next_h, hT] * self.G.u(hT, h.I.player)

    def _update_Sp(self):
        for I in self.running_uIs:
            for a in I.available_actions:
                self.S[I.id][a] += self.v[I.id, a] - self.v[I.id]
                self.Sp[I.id][a] = max(self.S[I.id][a], 0)

    def _update_σ(self):
        for I in self.running_uIs:
            actions = I.available_actions
            sp = self.Sp[I.id]
            normalize = sum(sp.values())
            if normalize > 0:
                d = {a: sp[a]/normalize for a in actions}
            else:
                l = len(actions)
                d = {a: 1/l for a in actions}
            self.σ[I.id] = d

    def _update_aσ(self):
        for I in self.running_uIs:
            for a in I.available_actions:
                self.sσ_num[I.id][a] += self.π[I.id]*self.σ[I.id][a]
                self.sσ_den[I.id][a] += self.π[I.id]
                self.aσ[I.id][a] = self.sσ_num[I.id][a]/self.sσ_den[I.id][a]