
from board_util import GoBoardUtil
INFINITY = 100000


def alphabeta(state, alpha, beta):
    if state.end_of_game():
        return state.evaluate(), None

    moves = state.get_best_moves()
    best_move = moves[0]

    for m in moves:
        # print("move: {} {}".format(m, state.current_player))

        # current = state.current_player
        # print(str(GoBoardUtil.get_twoD_board(state)) + '\n\n')
        state.play_move(m, state.current_player)
        value, _ = alphabeta(state, -beta, -alpha)
        value = -value
        # print(current, value, alpha, beta)
        if value > alpha:
            alpha = value
            best_move = m
        state.undo_move(m)
        # print(str(GoBoardUtil.get_twoD_board(state)) + '\n\n')
        if value >= beta:
            return beta, m
    return alpha, best_move


# initial call with full window
def call_alphabeta(rootState):
    print("STARTING PLAYER: {}".format(rootState.current_player))
    return alphabeta(rootState, -INFINITY, INFINITY)