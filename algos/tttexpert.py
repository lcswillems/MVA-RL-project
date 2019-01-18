import numpy as np

def pretty_grid(grid):
    display = ''
    for i in range(3):
        for j in range(3):
            if grid[i][j] == 1:
                display += ' x '
            elif grid[i][j] == 2:
                display += ' o '
            else:
                display += '   '
            if j < 2:
                display += "|"
        if i < 2:
            display += "\n-----------\n"
    return display

def TTT_optimal_σ(G):
    print("Computing optimal strategy...")

    σ = {}

    def aux_best_u(h):
        if h.I.terminal:
            return -G.u(h, h.I.player)
        else:
            actions = h.I.available_actions
            us = [aux_best_u(h.next(a)) for a in actions]
            σ[h.I.id] = actions[np.argmax(us)]
            return -np.max(us)

    aux_best_u(G.init_h)

    print("Optimal strategy computed.")

    return σ