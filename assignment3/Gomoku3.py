#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, PASS, EMPTY, BLACK, WHITE
from board import GoBoard
import numpy as np

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
        # all empyt points are legal in Gomoku
        # TODO: change to follow rules
        legalMoves = board.get_empty_points()

        # no more legal moves to pick from
        if legalMoves == []:
            return None

        # number of times the move has won
        numMoveWins = []
        for move in legalMoves:
            wins = self.simulate_move(boardCopy, move, color)
            numMoveWins.append(wins)

        # select the best move
        max_child = np.argmax(numMoveWins)
        return legalMoves[max_child]

    def simulate_move(self, board, move, color):
        wins = 0
        for _ in range(self.numSimulations):
            result = self.simulate(board, move, color)
            if result == color:
                win += 1
        return wins

    def simulate(self, board, move, color):
        boardCopy = board.copy()
        boardCopy.play_move()
        # first player played move, now opponent plays
        opponent = GoBoardUtil.opponent(color)
        return self.play_game(boardCopy, opponent)

    def play_game(self, board, color):
        passes = 0
        # simulate entire game to completion
        while board.detect_five_in_a_row() == EMPTY || board.get_empty_points() != []:
            color = board.current_player
            # TODO: filter moves by rules
            move = GoBoardUtil.generate_random_move(board, color)
            board.play_move(move, color)
            if move == PASS:
                passes += 1
            else:
                passes = 0 # reset number of consecutive passes
            if passes >= 2:
                break
        # return the winning colour
        return board.detect_five_in_a_row()

    @staticmethod
    def rule_based_move(board, color):
        """
        best move = None
        best move score = 0
        for each legal move:
            play move
            move score = check move
            if move score = 4 (win):
                return move
            if move score > best move score:
                best move = move
                best move score = move score
            undo move

        if best move is None:
            return random move
        return best move
        """

    @staticmethod
    def check_move(board, move, best_move_score):
        """
        returns if move is better than best move
        returns:
            4 if winning
            3 if block win
            2 if open four
            1 if block open four
            0 if random (otherwise)
        """

# compute upon new board size
def generate_lines(size):
    """
    boardLines = []
    for p in range(size * size):
        pointLines =
            horzontalLines(p) +
            verticalLines(p) +
            diag1Lines(p) +
            diag2Lines(p)
        boardLines.append(pointLines)
    return boardLines
    """

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
