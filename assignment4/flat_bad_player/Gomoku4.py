#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, PASS, EMPTY, BLACK, WHITE
from board import GoBoard
import random
import numpy as np

import cProfile

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
        emptyPoints = board.get_empty_points()

        # no more moves to pick from, so will pass
        if emptyPoints == []:
            return None

        # number of times the move has won
        numMoveWins = []
        bestMoves = self.rule_based_moves(board, color)
        for _, move in bestMoves:
            wins = self.simulate_move(board, move, color)
            numMoveWins.append(wins)

        # select the best move
        max_child = np.argmax(numMoveWins)
        return bestMoves[max_child][1]

    def simulate_move(self, board, move, color):
        wins = 0
        for _ in range(self.numSimulations):
            # simulate the move numSimulations times
            result = self.simulate(board, move, color)

            if result == color:
                wins += 1
        return wins

    def simulate(self, board, move, color):
        boardCopy = board.copy()
        boardCopy.play_move(move, color)
        # return the color if they won
        # if board.check_win(move) == color:
        #     return color
        # first player played move, now opponent plays
        opponent = GoBoardUtil.opponent(color)
        
        passes = 0
        winningColor = EMPTY

        # simulate entire game to completion
        while boardCopy.get_empty_points() != []:
            color = boardCopy.current_player
            bestMoves = self.rule_based_moves(boardCopy, color)

            moveScore, move = random.choice(bestMoves)

            # return color if they won
            if moveScore == WIN:
                return color
            
            boardCopy.play_move(move, color)
            if move == PASS:
                passes += 1
            else:
                passes = 0 # reset number of consecutive passes
            if passes >= 2:
                break

        # return the winning colour
        return winningColor

    def rule_based_moves(self, board, color):
        moveResults = []

        for move in board.get_empty_points():
            moveScore = self.check_move(board, color, move)
            moveResults.append((moveScore, move))

        moveResults.sort(reverse = True, key = lambda x: x[0])

        # get best moves
        bestMoves = []
        bestMoveScore = RANDOM
        for move in moveResults:
            if move[0] > bestMoveScore:
                bestMoveScore = move[0]
            if move[0] < bestMoveScore:
                break
            bestMoves.append(move)

        return bestMoves

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
                    bestOppMoves = self.rule_based_moves(board, oppColor)
                    # We know there are moves left in this case
                    if bestOppMoves[0][0] < OPEN_FOUR:
                        isBlockOpenFour = True
                else:
                    isBlockOpenFour = True
                
                if isBlockOpenFour:
                    maxScore = max(BLOCK_OPEN_FOUR, maxScore)

        board.undo_move(move)

        return maxScore

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)
    con.start_connection()
    

if __name__ == "__main__":
    # run()
    cProfile.run('run()')
