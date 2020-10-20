
from board_util import GoBoardUtil
from gtp_connection import format_point, point_to_coord
INFINITY = 100000


def alphabeta(state, alpha, beta, tTable, hasher):

    hashCode = hasher.hash(GoBoardUtil.get_oneD_board(state))
    result = tTable.lookup(hashCode)

    if result != None:
        return result, None

    if state.end_of_game():
        result = state.evaluate()
        storeResult(tTable,hashCode,result)
        return result, None

    moves = state.get_best_moves()
    best_move = moves[0]

    for m in moves:
        state.play_move(m, state.current_player)
        value, _ = alphabeta(state, -beta, -alpha, tTable, hasher)
        value = -value
        if value > alpha:
            alpha = value
            best_move = m
  """       hashCodeNew1 = hasher.hash(GoBoardUtil.get_oneD_board(state))
            storeResult(tTable,hashCode,alpha)
            if alpha == INFINITY:
                return alpha, best_move """
        state.undo_move(m)
        if value >= beta:
            hashCodeNew2 = hasher.hash(GoBoardUtil.get_oneD_board(state))
            storeResult(tTable,hashCode,beta)
            return beta, m
    
    storeResult(tTable,hashCode,alpha)
    return alpha, best_move


# initial call with full window
def call_alphabeta(rootState, tTable, hasher):
    # best_moves = rootState.get_best_moves()
    # best_moves = list(map(lambda p: format_point(point_to_coord(p, rootState.size)), best_moves))
    # print("best moves: {}".format(best_moves))
    return alphabeta(rootState, -INFINITY, INFINITY, tTable, hasher)


def storeResult(tTable, code, result):
    tTable.store(code, result)
    return result