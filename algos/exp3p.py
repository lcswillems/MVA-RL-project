import numpy as np

class Exp3P:
    """Exp3.P algorithm."""

    def __init__(self, actions, η, γ, β):
        self._actions = actions
        self._nb_actions = len(self._actions)
        self.η = η
        self.γ = γ
        self.β = β

        self.T = 0
        self._init_w()
        self._init_π_aπ()

    def _init_w(self):
        self.w = np.ones(self._nb_actions)

    def _init_π_aπ(self):
        self._π = (1-self.γ) * self.w / np.sum(self.w) + self.γ / self._nb_actions
        self.π = {self._actions[i]: self._π[i] for i in range(self._nb_actions)}
        self.sπ = {a: 0 for a in self._actions}
        self.aπ = {a: self.π[a] for a in self._actions}

    def play(self):
        self.a = np.random.choice(self._actions, 1, p=self._π)[0]
        return self.a

    def update_policy(self, u_a):
        self.T += 1
        hot = np.array([int(self.a == i) for i in range(self._nb_actions)])
        u2 = (u_a*hot + self.β)/self._π
        self._update_w(u2)

    def _update_w(self, u):
        self.w *= np.exp(self.η * u)
        self._update_π_aπ()

    def _update_π_aπ(self):
        self._π = (1-self.γ) * self.w / np.sum(self.w) + self.γ / self._nb_actions
        self.π = {self._actions[i]: self._π[i] for i in range(self._nb_actions)}
        self.sπ[self.a] += 1
        self.aπ = {a: self.sπ[a]/self.T for a in self._actions}