#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, PASS, EMPTY, BLACK, WHITE
from board import GoBoard
import numpy as np

WIN = 4
BLOCK_WIN = 3
OPEN_FOUR = 2
BLOCK_OPEN_FOUR = 1
RANDOM = 0

class Gomoku():
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
        self.name = "GomokuAssignment3"
        self.version = 1.0
        self.numSimulations = 10

    def get_move(self, board, color):
        # generate a move using one-ply MC simulations
        boardCopy = board.copy()
        emptyPoints = board.get_empty_points()

        # no more moves to pick from, so will pass
        if len(emptyPoints) == 0:
            return None

        # number of times the move has won
        numMoveWins = []
        for move in emptyPoints:
            wins = self.simulate_move(boardCopy, move, color)
            numMoveWins.append(wins)

        # select the best move
        max_child = np.argmax(numMoveWins)
        return emptyPoints[max_child]

    def simulate_move(self, board, move, color):
        wins = 0
        for _ in range(self.numSimulations):
            result = self.simulate(board, move, color)
            if result == color:
                wins += 1
        return wins

    def simulate(self, board, move, color):
        boardCopy = board.copy()
        boardCopy.play_move(move, color)
        # first player played move, now opponent plays
        opponent = GoBoardUtil.opponent(color)
        return self.play_game(boardCopy, opponent)

    def play_game(self, board, color):
        passes = 0

        # simulate entire game to completion
        while board.detect_five_in_a_row() == EMPTY and len(board.get_empty_points()) != 0:
            color = board.current_player
            # TODO: filter moves by rules
            move = self.rule_based_move(board, color)
            board.play_move(move, color)
            if move == PASS:
                passes += 1
            else:
                passes = 0 # reset number of consecutive passes
            if passes >= 2:
                break
        # return the winning colour
        return board.detect_five_in_a_row()

    def rule_based_move(self, board, color):
        """
        returns best move for color
        """
        bestMove = None
        bestMoveScore = RANDOM
        # print(board.get_empty_points())


        for move in board.get_empty_points():
            moveScore = self.check_move(board, color, move)
            if moveScore == WIN:
                return move
            if moveScore > bestMoveScore:
                bestMove = move
                bestMoveScore = moveScore

        if bestMove is None:
            return GoBoardUtil.generate_random_move(board, color)
        else:
            return bestMove

    def check_move(self, board, color, move):
        """
        returns:
            4 if winning
            3 if block win
            2 if open four
            1 if block open four
            0 otherwise (random)
        """
        newpoint = board.unpadded_point(move)
        lines = board.boardLines[newpoint]
        maxScore = RANDOM
        for line in lines:
            counts = self.get_counts(board, line)
            if color == BLACK:
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts

            if myCount == 4:
                return WIN
            elif oppCount == 4:
                maxScore = max(BLOCK_WIN, maxScore)
            elif myCount == 3 and oppCount == 0:
                maxScore = max(OPEN_FOUR, maxScore)
            elif myCount == 0 and oppCount == 3:
                maxScore = max(BLOCK_OPEN_FOUR, maxScore)
            else:
                maxScore = max(RANDOM, maxScore)

        return maxScore

    @staticmethod
    def get_counts(board, five_line):
        b_count = 0
        w_count = 0
        e_count = 0

        for p in five_line:
            stone = board.board[p]
            if stone == BLACK:
                b_count += 1
            elif stone == WHITE:
                w_count += 1
            else:
                e_count += 1

        return b_count, w_count, e_count


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)
    con.start_connection()
    

if __name__ == "__main__":
    run()
