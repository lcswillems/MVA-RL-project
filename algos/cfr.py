import numpy as np

# All the notations are taken from: http://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf.
# The code only works for perfect recall games.

class CFR:
    """CFR algorithm."""

    def __init__(self, G):
        self.G = G
        self._cache_tree_game()

        self.T = 0
        self._init_v()
        self._init_Sp()
        self._init_σ_aσ()

    def _cache_tree_game(self):
        print("Caching game tree...")

        self.G.uIs = set()
        self.G.hTs = []

        stack = [self.G.init_h]
        while len(stack) != 0:
            h = stack.pop()
            if h.I.terminal:
                self.G.hTs.append(h)
            else:
                self.G.uIs.add(h.I)
            for a in h.I.available_actions:
                next_h = h.next(a)
                stack.append(next_h)

        print("Tree cached.")

    def _init_v(self):
        # v[I.id] gives u'_i(σ, I) where i = I.player.
        # v[I.id, a] gives u'_i(σ|I->a, I) where i = I.player.
        self.v = {}
        for I in self.G.uIs:
            self.v[I.id] = 0
            for a in I.available_actions:
                self.v[I.id, a] = 0

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
        self.sσ = {}
        # σa[I.id][a] gives the average σ_i(I)(a) where i = I.player.
        self.aσ = {}
        for I in self.G.uIs:
            l = len(I.available_actions)
            self.σ[I.id] = {a: 1/l for a in I.available_actions}
            self.sσ[I.id] = {a: 0 for a in I.available_actions}
            self.aσ[I.id] = {a: self.σ[I.id][a] for a in I.available_actions}

    def update_policy(self):
        self.T += 1
        self._update_v()
        self._update_Sp()
        self._update_σ_aσ()

    def _update_v(self):
        self._init_v()

        # π_[i, h] gives π^σ_{-i}(h).
        π_ = {}

        # π[h, hT] gives π^σ(h, hT).
        π = {}

        h = self.G.init_h
        for i2 in range(self.G.nb_players):
            π_[i2, h] = 1
        stack = [h]
        while len(stack) != 0:
            h = stack.pop()
            i = h.player
            for a in h.I.available_actions:
                next_h = h.next(a)
                stack.append(next_h)
                for i2 in range(self.G.nb_players):
                    p = 1 if i == i2 else self.σ[h.I.id][a]
                    π_[i2, next_h] = π_[i2, h] * p

        for hT in self.G.hTs:
            π[hT, hT] = 1
            h = hT

            while not h.I.initial:
                next_h = h
                h, a = next_h.previous

                π[h, hT] = self.σ[h.I.id][a] * π[next_h, hT]

                self.v[h.I.id] += π_[h.player, h] * π[h, hT] * self.G.u(hT, h.I.player)
                self.v[h.I.id, a] += π_[h.player, h] * π[next_h, hT] * self.G.u(hT, h.I.player)

    def _update_Sp(self):
        for I in self.G.uIs:
            for a in I.available_actions:
                self.S[I.id][a] += self.v[I.id, a] - self.v[I.id]
                self.Sp[I.id][a] = max(self.S[I.id][a], 0)

    def _update_σ_aσ(self):
        for I in self.G.uIs:
            actions = I.available_actions

            # Update σ
            sp = self.Sp[I.id]
            normalize = sum(sp.values())
            if normalize > 0:
                d = {a: sp[a]/normalize for a in actions}
            else:
                l = len(actions)
                d = {a: 1/l for a in actions}
            self.σ[I.id] = d

            # Update sσ & aσ
            normalize = self.T*(self.T+1)/2
            for a in actions:
                self.sσ[I.id][a] += self.T*self.σ[I.id][a]
                self.aσ[I.id][a] = self.sσ[I.id][a]/normalize