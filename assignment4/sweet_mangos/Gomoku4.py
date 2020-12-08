import sys
import signal
from gtp_connection import GtpConnection
from board_util import GoBoardUtil, PASS, EMPTY, BLACK, WHITE
from board import GoBoard
from evaluation import evaluate
from mcts import MctsTree, mcts_step

import cProfile

WIN = 4
BLOCK_WIN = 3
OPEN_FOUR = 2
BLOCK_OPEN_FOUR = 1
RANDOM = 0


class TimeoutException(Exception):
    pass


def handler(signum, frame):
    raise TimeoutException


signal.signal(signal.SIGALRM, handler)


class HeuristicPolicy:

    def best_moves(self, board, color):
        moves = board.get_empty_points()
        moveResults = list(map(lambda m: (m, self._move_score(board, color, m)), moves))
        return sorted(moveResults, key=lambda r: r[1], reverse=True)

    def _move_score(self, board, color, m):
        board.play_move(m, board.current_player)
        score = evaluate(board, color)
        board.undo_move(m)
        return score


class RulePolicy:

    def best_moves(self, board, color):
        moveResults = []

        for move in board.get_empty_points():
            moveScore = self.check_move(board, color, move)
            moveResults.append((move, moveScore))

        moveResults.sort(reverse=True, key=lambda x: x[1])
        return moveResults

    def check_move(self, board, color, move):
        """
        returns:
            4 if winning
            3 if block win
            2 if open four
            1 if block open four
            0 otherwise (random)
        """

        board.play_move(move, color)

        newPoint = board.unpadded_point(move)
        lines5 = board.boardLines5[newPoint]
        maxScore = RANDOM
        for line in lines5:
            counts = board.get_counts(line)
            if color == BLACK:
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts

            if myCount == 5:
                board.undo_move(move)
                return WIN
            elif oppCount == 4 and myCount == 1:
                maxScore = max(BLOCK_WIN, maxScore)

        lines6 = board.boardLines6[newPoint]
        oppColor = GoBoardUtil.opponent(color)
        for line in lines6:
            counts = board.get_counts(line)
            if color == BLACK:
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts

            firstColor = board.board[line[0]]
            lastColor = board.board[line[-1]]

            if myCount == 4 and firstColor == EMPTY and lastColor == EMPTY:
                maxScore = max(OPEN_FOUR, maxScore)
            elif myCount == 1 and oppCount == 3 and firstColor != oppColor and lastColor != oppColor:
                isBlockOpenFour = False

                colorLine = tuple(map(lambda m: board.board[m], line))
                # must hard code these two cases, they are the only six line patterns that match
                # the above rule, but do not necessarily block an open four
                if colorLine == (color, EMPTY, oppColor, oppColor, oppColor, EMPTY) or \
                   colorLine == (EMPTY, oppColor, oppColor, oppColor, EMPTY, color):

                    # There are alot of edge cases here, so we play the move for
                    # the opposite color and check if they still have an open four available to them
                    # This may break if there are multiple open fours, which wouldn't happen
                    # if the rule based policy is followed throughout the game
                    bestOppMoves = self.best_moves(board, oppColor)
                    # We know there are moves left in this case
                    if bestOppMoves[0][1] < OPEN_FOUR:
                        isBlockOpenFour = True
                else:
                    isBlockOpenFour = True

                if isBlockOpenFour:
                    maxScore = max(BLOCK_OPEN_FOUR, maxScore)

        board.undo_move(move)

        return maxScore


class CombinedPolicy:
    def __init__(self):
        self.rule_policy = RulePolicy()
        self.h_policy = HeuristicPolicy()

    def best_moves(self, board, color):
        rule_best_moves = self.rule_policy.best_moves(board, color)

        # get best moves
        best_moves = []
        best_move_score = RANDOM
        for move in rule_best_moves:
            if move[1] > best_move_score:
                best_move_score = move[1]
            if move[1] < best_move_score or move[1] == RANDOM:
                break
            best_moves.append(move)

        if len(best_moves) > 0:
            return best_moves

        return self.h_policy.best_moves(board, color)


class Gomoku:
    def __init__(self):
        """
        Gomoku player that selects moves randomly from the set of legal moves.
        Passes/resigns only at the end of the game.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "GomokuAssignment4"
        self.version = 1.0
        self.timelimit = 59

    def set_timeout(self, limit):
        self.timelimit = limit

    def get_move(self, board, color):
        signal.alarm(self.timelimit)  # sets an alarm for the given time_limit

        try:
            mcts_tree = MctsTree(board, color, CombinedPolicy())
            while True:
                # print(mcts_tree)
                mcts_step(mcts_tree)

        except TimeoutException:
            # print(mcts_tree)
            return mcts_tree.best_move()
        except Exception:
            return mcts_tree.best_move()
        finally:
            signal.alarm(0)  # disable the alarm


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)

    if len(sys.argv) >= 4 and sys.argv[1] == '--pycharm':
        filename = sys.argv[3]
        with open(filename, 'r') as f:
            con.start_connection(f)
    else:
        con.start_connection(sys.stdin)
    

if __name__ == "__main__":
    run()
    # cProfile.run('run()')
