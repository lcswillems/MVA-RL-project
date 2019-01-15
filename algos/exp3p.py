import numpy as np

class Exp3P:
    """Exp3.P algorithm."""

    def __init__(self, nb_actions, η, γ, β):
        self._nb_actions = nb_actions
        self.η = η
        self.γ = γ
        self.β = β

        self.actions = np.arange(self.nb_actions)
        self.w = 0.01 * np.ones(self.nb_actions)
        self.w[np.random.randint(nb_actions)] = 1

    @property
    def nb_actions(self):
        return self._nb_actions

    def play(self):
        self.σ = (1-self.γ) * self.w / np.sum(self.w) + self.γ / self.nb_actions
        self.a = np.random.choice(self.actions, 1, p=self.σ)[0]
        return self.a

    def analyze_feedback(self, u):
        hot = np.array([int(self.a == i) for i in range(self.nb_actions)])
        u2 = (u*hot + self.β)/self.σ[self.a]
        self.w *= np.exp(self.η * u2)