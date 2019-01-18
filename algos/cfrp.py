from .cfr import CFR

class CFRp(CFR):
    def _update_Sp(self):
        for I in self.G.uIs:
            for a in I.available_actions:
                self.S[I.id][a] = self.Sp[I.id][a] + self.v[I.id, a] - self.v[I.id]
                self.Sp[I.id][a] = max(self.S[I.id][a], 0)

    def _update_aσ(self):
        for I in self.G.uIs:
            for a in I.available_actions:
                self.sσ_num[I.id][a] += self.T*self.σ[I.id][a]
                self.sσ_den[I.id][a] += self.T
                self.aσ[I.id][a] = self.sσ_num[I.id][a]/self.sσ_den[I.id][a]