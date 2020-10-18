#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection, color_to_string, format_point, point_to_coord
from board_util import GoBoardUtil
from board import GoBoard
from alphabeta import call_alphabeta


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
        self.name = "GomokuAssignment2"
        self.version = 1.0

    def get_move(self, board, color):
        outcome, move = self.solve(board)

        if move is not None:
            return move
        else:
            return GoBoardUtil.generate_random_move(board, color)

    def solve(self, board):
        score, move = call_alphabeta(board)

        if score == 0:
            return "draw", move
        else:
            if score > 0:
                winner = board.current_player
                return color_to_string(winner), move
            else:
                winner = GoBoardUtil.opponent(board.current_player)
                # We only display the move if the current player wins
                return color_to_string(winner), None


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
