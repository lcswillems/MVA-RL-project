from tqdm import tqdm

from games import TicTacToe

N = 10

G = TicTacToe()
print("Caching game tree...")
G.cache_tree()

# All the notations are taken from: http://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf.
# The code only works for perfect recall games.

def σ_to_u2(σ):
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

    for I in G.Is:
        u2[I] = 0
        for a in I.available_actions:
            u2[I, a] = 0

    h = G.initial_history
    for i2 in range(G.nb_players):
        π_[i2, h] = 1
    stack = [h]
    while len(stack) != 0:
        h = stack.pop()
        i = h.player
        for a in h.I.available_actions:
            next_h = h.next(a)
            stack.append(next_h)
            for i2 in range(G.nb_players):
                p = 1 if i == i2 else σ[h.I][a]
                π_[i2, next_h] = π_[i2, h] * p

    for hT in G.hTs:
        π[hT, hT] = 1

        next_h = hT
        h, a = next_h.previous
        while not h.I.initial:
            π[h, hT] = σ[h.I][a] * π[next_h, hT]

            u2[h.I] += π_[h.player, h] * π[h, hT] * hT.I.u(i)
            u2[h.I, a] += π_[h.player, h] * π[next_h, hT] * hT.I.u(i)

            next_h = h
            h, a = next_h.previous

    return u2

def u2s_to_R(u2s):
    # R[I][a] gives R_i^{T,+}(I, a) where i = I.player.
    R = {}

    T = len(u2s)

    for I in G.Is:
        R[I] = {}
        for a in I.available_actions:
            R[I][a] = 1/T * max(sum([u2s[t][I, a] - u2s[t][I] for t in range(T)]), 0)

    return R

def R_to_σ(R):
    # σ[I][a] gives σ_i(I)(a) where i = I.player.
    σ = {}

    for I in G.Is:
        r = R[I]
        s = sum(r.values())
        if s > 0:
            d = {a: r[a]/s for a in r.keys()}
        else:
            actions = r.keys()
            l = len(actions)
            d = {a: 1/l for a in actions}
        σ[I] = d

    return σ

def uniform_σ():
    σ = {}

    for I in G.Is:
        actions = I.available_actions
        l = len(actions)
        σ[I] = {a: 1/l for a in actions}

    return σ

σ = uniform_σ()
u2s = []

print("Computing σ...")
for T in tqdm(range(N)):
    u2s.append(σ_to_u2(σ))
    R = u2s_to_R(u2s)
    σ = R_to_σ(R)