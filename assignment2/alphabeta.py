
from board_util import GoBoardUtil
from gtp_connection import format_point, point_to_coord
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
        state.undo_move(m)
        if value >= beta:
            return beta, m
    return alpha, best_move


# initial call with full window
def call_alphabeta(rootState):
    # best_moves = rootState.get_best_moves()
    # best_moves = list(map(lambda p: format_point(point_to_coord(p, rootState.size)), best_moves))
    # print("best moves: {}".format(best_moves))
    return alphabeta(rootState, -INFINITY, INFINITY)