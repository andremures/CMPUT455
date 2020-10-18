
INFINITY = 100000


def alphabeta(state, alpha, beta):
    if state.end_of_game():
        return state.evaluate(), None

    moves = state.get_best_moves()
    best_move = moves[0]

    for m in moves:
        state.play_move(m, state.current_player)
        value, _ = alphabeta(state, -beta, -alpha)
        value = -value
        if value > alpha:
            alpha = value
            best_move = m
        state.undo_move()
        if value >= beta:
            return beta, m
    return alpha, best_move


# initial call with full window
def call_alphabeta(rootState):
    return alphabeta(rootState, -INFINITY, INFINITY)