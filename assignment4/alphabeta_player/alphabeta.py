
from board_util import GoBoardUtil
INFINITY = 100000


def alphabeta(state, alpha, beta, tt, hasher):
    hashCode = hasher.hash(GoBoardUtil.get_oneD_board(state))
    result = tt.lookup(hashCode)

    if result is not None:
        return result

    if state.end_of_game():
        result = state.evaluate(), None
        storeResult(tt, hashCode, result)
        return result

    moves = state.get_best_moves()
    best_move = moves[0]

    for m in moves:
        state.play_move(m, state.current_player)
        value, _ = alphabeta(state, -beta, -alpha, tt, hasher)
        value = -value
        if value > alpha:
            alpha = value
            best_move = m
        state.undo_move(m)
        if value >= beta:
            result = beta, m
            storeResult(tt, hashCode, result)
            return result

    result = alpha, best_move
    storeResult(tt, hashCode, result)
    return result


# initial call with full window
def call_alphabeta(rootState, tt, hasher):
    return alphabeta(rootState, -INFINITY, INFINITY, tt, hasher)


def storeResult(tt, code, result):
    tt.store(code, result)
    return result