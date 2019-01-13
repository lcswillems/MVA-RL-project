G = ...
G.cache_tree()
N = ...

def σ_to_u2(σ):
    # π_[i, h] gives π^σ_{-i}(h).
    π_ = {}

    # π[h, hT] gives π^σ(h, hT).
    # π[h, hT, i, I, a] gives π^{σ'}(h, hT)
    #       where σ' is a strategy profile identical to σ except that
    #       player i always chooses action a when in information set I.
    π = {}

    # u2[i, I] gives u'_i(σ, I).
    # u2[i, I, a] gives u'_i(σ|I->a, I).
    u2 = {}

    for i in range(G.nb_players):
        for I in G.Is:
            u2[i, I] = 0
            for a in I.available_actions:
                u2[i, I, a] = 0

    h = G.initial_history
    for i2 in range(G.nb_players):
        π_[i2, h] = 1
    queue = [h]
    while len(queue) != 0:
        h = queue.pop(0)
        i = h.player
        for a in h.I.available_actions:
            next_h = h.next(a)
            for i2 in range(G.nb_players):
                p = 1 if i == i2 else σ[i, h.I]
                π_[i2, next_h] = π_[i2, h] * p

    for hT in G.hTs:
        π[hT, hT] = 1

        next_h = hT
        h, a = next_h.previous()
        while not h.is_initial():
            i = h.player

            π[h, hT] = σ[i, h.I][a] * π[next_h, hT]

            u2[i, h.I] += π_[i, h] * π[h, hT] * hT.u(i)
            u2[i, h.I, a] += π_[i, h] * π[next_h, hT] * hT.u(i)

            next_h = h
            h, a = next_h.previous()

    return u2

def u2s_to_R(u2s):
    # R[i, I][a] gives R_i^{T,+}(I, a).
    R = {}

    T = len(u2s)

    for i in range(G.nb_players):
        for I in G.Is:
            R[i, I] = {}
            for a in I.available_actions:
                R[i, I][a] = 1/T * max(sum([u2s[t][i, I, a] - u2s[t][i, I] for t in range(T)]), 0)

    return R

def R_to_σ(R):
    # σ[i, I][a] gives σ_i(I)(a).
    σ = {}

    for i, I in R.keys():
        r = R[i, I]
        s = sum(r.values())
        if s > 0:
            d = {a: r[a]/s for a in r.keys()}
        else:
            actions = r.keys()
            l = len(actions)
            d = {a: 1/l for a in actions}
        σ[i, I] = d

    return σ

def uniform_σ():
    σ = {}

    for i in range(G.nb_players):
        for I in G.Is:
            actions = I.available_actions
            l = len(actions)
            σ[i, I] = {a: 1/l for a in actions}

    return σ

σs = [None] * N
u2s = [None] * (N-1)
Rs = [None] * (N-1)

σs[0] = uniform_σ()

for T in range(N-1):
    u2s[T] = σ_to_u2(σs[T])
    Rs[T] = u2s_to_R(u2s)
    σs[T+1] = R_to_σ(Rs[T])