import numpy as np

class Exp3P:
    """Exp3.P algorithm."""

    def __init__(self, actions, η, γ, β):
        self._actions = actions
        self._nb_actions = len(self._actions)
        self.η = η
        self.γ = γ
        self.β = β

        self.w = np.ones(self._nb_actions)
        self._update_policy()

    def play(self):
        self.a = np.random.choice(self._actions, 1, p=self._π)[0]
        return self.a

    def update_policy(self, u_a):
        hot = np.array([int(self.a == i) for i in range(self._nb_actions)])
        u2 = (u_a*hot + self.β)/self._π
        self._update_weights(u2)

    def _update_weights(self, u):
        self.w *= np.exp(self.η * u)
        self._update_policy()

    def _update_policy(self):
        self._π = (1-self.γ) * self.w / np.sum(self.w) + self.γ / self._nb_actions
        self.π = {self._actions[i]: self._π[i] for i in range(self._nb_actions)}