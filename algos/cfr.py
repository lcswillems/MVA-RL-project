import numpy as np

# All the notations are taken from: http://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf.
# The code only works for perfect recall games.

class CFR:
    """CFR algorithm."""

    def __init__(self, G, init_policies="uniform"):
        self.G = G
        self._cache_tree_game()
        self.T = 0

        if init_policies == "uniform":
            self.σ = self._uniform_policies()
        elif init_policies == "hot":
            self.σ = self._hot_policies()
        else:
            raise ValueError("`{}` is not a correct value for `init_policies`.".format(init_policies))

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

    def _σ_to_u2(self, σ):
        # π_[i, h] gives π^σ_{-i}(h).
        π_ = {}

        # π[h, hT] gives π^σ(h, hT).
        # π[h, hT, I, a] gives π^{σ'}(h, hT)
        #       where σ' is a strategy profile identical to σ except that
        #       player I.player always chooses action a when in information set I.
        π = {}

        # u2[I] gives u'_i(σ, I) where i = I.player.
        # u2[I, a] gives u'_i(σ|I->a, I) where i = I.player.
        u2 = {}

        for I in self.G.uIs:
            u2[I] = 0
            for a in I.available_actions:
                u2[I, a] = 0

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
                    p = 1 if i == i2 else σ[h.I.id][a]
                    π_[i2, next_h] = π_[i2, h] * p

        for hT in self.G.hTs:
            π[hT, hT] = 1
            h = hT

            while not h.I.initial:
                next_h = h
                h, a = next_h.previous

                π[h, hT] = σ[h.I.id][a] * π[next_h, hT]

                u2[h.I] += π_[h.player, h] * π[h, hT] * self.G.u(hT, h.I.player)
                u2[h.I, a] += π_[h.player, h] * π[next_h, hT] * self.G.u(hT, h.I.player)

        return u2

    def _u2_to_R(self, u2):
        if not hasattr(self, 'S'):
            self.S = {}
            for I in self.G.uIs:
                self.S[I.id] = {}
                for a in I.available_actions:
                    self.S[I.id][a] = 0

        # R[I.id][a] gives R_i^{T,+}(I, a) where i = I.player and T = self.T.
        R = {}

        for I in self.G.uIs:
            R[I.id] = {}
            for a in I.available_actions:
                self.S[I.id][a] += u2[I, a] - u2[I]
                R[I.id][a] = 1/self.T * max(self.S[I.id][a], 0)

        return R

    def _R_to_σ(self, R):
        # σ[I.id][a] gives σ_i(I)(a) where i = I.player.
        σ = {}

        for I in self.G.uIs:
            r = R[I.id]
            s = sum(r.values())
            if s > 0:
                d = {a: r[a]/s for a in r.keys()}
            else:
                actions = r.keys()
                l = len(actions)
                d = {a: 1/l for a in actions}
            σ[I.id] = d

        return σ

    def _uniform_policies(self):
        σ = {}

        for I in self.G.uIs:
            actions = I.available_actions
            l = len(actions)
            σ[I.id] = {a: 1/l for a in actions}

        return σ

    def _hot_policies(self):
        σ = {}

        for I in self.G.uIs:
            actions = I.available_actions
            hot_a = np.random.choice(actions)
            σ[I.id] = {a: (1 if a == hot_a else 0) for a in actions}

        return σ

    def update_policies(self):
        self.T += 1
        self.u2 = self._σ_to_u2(self.σ)
        self.R = self._u2_to_R(self.u2)
        self.σ = self._R_to_σ(self.R)