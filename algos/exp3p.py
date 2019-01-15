import numpy as np

class Exp3P:
    """Exp3.P algorithm."""

    def __init__(self, actions, η, γ, β, init_weights="uniform"):
        self._actions = actions
        self._nb_actions = len(self._actions)
        self.η = η
        self.γ = γ
        self.β = β

        if init_weights == "uniform":
            self.w = self._uniform_weights()
        elif init_weights == "hot":
            self.w = self._hot_weights()
        else:
            raise ValueError("`{}` is not a correct value for `init_weights`.".format(init_weights))

        self._update_policy()

    def _uniform_weights(self):
        return np.ones(self._nb_actions)

    def _hot_weights(self):
        w = 0.01 * np.ones(self._nb_actions)
        w[np.random.randint(self._nb_actions)] = 1
        return w

    def _update_policy(self):
        self._π = (1-self.γ) * self.w / np.sum(self.w) + self.γ / self._nb_actions
        self.π = {self._actions[i]: self._π[i] for i in range(self._nb_actions)}

    def play(self):
        self.a = np.random.choice(self._actions, 1, p=self._π)[0]
        return self.a

    def analyze_feedback(self, u):
        hot = np.array([int(self.a == i) for i in range(self._nb_actions)])
        u2 = (u*hot + self.β)/self._π
        self.w *= np.exp(self.η * u2)
        self._update_policy()