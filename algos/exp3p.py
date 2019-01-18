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
        self._init_σi_aσi()

    def _init_w(self):
        self.w = np.ones(self._nb_actions)

    def _init_σi_aσi(self):
        self._σi = (1-self.γ) * self.w / np.sum(self.w) + self.γ / self._nb_actions
        self.σi = {self._actions[i]: self._σi[i] for i in range(self._nb_actions)}
        self.sσi = {a: 0 for a in self._actions}
        self.aσi = {a: self.σi[a] for a in self._actions}

    def play(self):
        self.a = np.random.choice(self._actions, 1, p=self._σi)[0]
        return self.a

    def update_policy(self, u_a):
        self.T += 1
        hot = np.array([int(self.a == i) for i in range(self._nb_actions)])
        u2 = (u_a*hot + self.β)/self._σi
        self._update_w(u2)

    def _update_w(self, u):
        self.w *= np.exp(self.η * u)
        self._update_σi_aσi()

    def _update_σi_aσi(self):
        self._σi = (1-self.γ) * self.w / np.sum(self.w) + self.γ / self._nb_actions
        self.σi = {self._actions[i]: self._σi[i] for i in range(self._nb_actions)}
        for a in self._actions:
            self.sσi[a] += self.σi[a]
            self.aσi[a] = self.sσi[a]/self.T