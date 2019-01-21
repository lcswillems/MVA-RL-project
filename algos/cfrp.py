from .cfr import CFR

class CFRp(CFR):
    def update_policy(self):
        self.T += 1
        for i in self.G.player_uIs.keys():
            self.running_uIs = self.G.player_uIs[i]
            self._compute_v()
            self._update_Sp()
            self._update_σ()
            self._update_aσ()

    def _update_Sp(self):
        for I in self.running_uIs:
            for a in I.available_actions:
                self.S[I.id][a] = self.Sp[I.id][a] + self.v[I.id, a] - self.v[I.id]
                self.Sp[I.id][a] = max(self.S[I.id][a], 0)

    def _update_aσ(self):
        for I in self.running_uIs:
            for a in I.available_actions:
                self.sσ_num[I.id][a] += self.T*self.σ[I.id][a]
                self.sσ_den[I.id][a] += self.T
                self.aσ[I.id][a] = self.sσ_num[I.id][a]/self.sσ_den[I.id][a]