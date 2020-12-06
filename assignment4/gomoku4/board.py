"""
board.py

Implements a basic Go board with functions to:
- initialize to a given board size
- check if a move is legal
- play a move

The board uses a 1-dimensional representation with padding
"""

import numpy as np
from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    PASS,
    is_black_white,
    is_black_white_empty,
    coord_to_point,
    where1d,
    MAXSIZE,
    GO_POINT
)

"""
The GoBoard class implements a board and basic functions to play
moves, check the end of the game, and count the acore at the end.
The class also contains basic utility functions for writing a Go player.
For many more utility functions, see the GoBoardUtil class in board_util.py.

The board is stored as a one-dimensional array of GO_POINT in self.board.
See GoBoardUtil.coord_to_point for explanations of the array encoding.
"""
class GoBoard(object):
    def __init__(self, size):
        """
        Creates a Go board of given size
        """
        assert 5 <= size <= MAXSIZE
        self.reset(size)

    def calculate_rows_cols_diags(self):
        if self.size < 5:
            return
        # precalculate all rows, cols, and diags for 5-in-a-row detection
        self.rows = []
        self.cols = []

    def calculate_rows_cols_diags(self):
        if self.size < 5:
            return
        # precalculate all rows, cols, and diags for 5-in-a-row detection
        self.rows = []
        self.cols = []
        for i in range(1, self.size + 1):
            current_row = []
            start = self.row_start(i)
            for pt in range(start, start + self.size):
                current_row.append(pt)
            self.rows.append(current_row)

            start = self.row_start(1) + i - 1
            current_col = []
            for pt in range(start, self.row_start(self.size) + i, self.NS):
                current_col.append(pt)
            self.cols.append(current_col)

        self.diags = []
        # diag towards SE, starting from first row (1,1) moving right to (1,n)
        start = self.row_start(1)
        for i in range(start, start + self.size):
            diag_SE = []
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_SE.append(pt)
                pt += self.NS + 1
            if len(diag_SE) >= 5:
                self.diags.append(diag_SE)
        # diag towards SE and NE, starting from (2,1) downwards to (n,1)
        for i in range(start + self.NS, self.row_start(self.size) + 1, self.NS):
            diag_SE = []
            diag_NE = []
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_SE.append(pt)
                pt += self.NS + 1
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_NE.append(pt)
                pt += -1 * self.NS + 1
            if len(diag_SE) >= 5:
                self.diags.append(diag_SE)
            if len(diag_NE) >= 5:
                self.diags.append(diag_NE)
        # diag towards NE, starting from (n,2) moving right to (n,n)
        start = self.row_start(self.size) + 1
        for i in range(start, start + self.size):
            diag_NE = []
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_NE.append(pt)
                pt += -1 * self.NS + 1
            if len(diag_NE) >=5:
                self.diags.append(diag_NE)
        assert len(self.rows) == self.size
        assert len(self.cols) == self.size
        assert len(self.diags) == (2 * (self.size - 5) + 1) * 2

    def reset(self, size):
        """
        Creates a start state, an empty board with given size.
        """
        self.size = size
        self.NS = size + 1
        self.WE = 1
        self.ko_recapture = None
        self.last_move = None
        self.last2_move = None
        self.current_player = BLACK
        self.maxpoint = size * size + 3 * (size + 1)
        self.board = np.full(self.maxpoint, BORDER, dtype=GO_POINT)
        self._initialize_empty_points(self.board)
        self.calculate_rows_cols_diags()
        self.boardLines5 = self.generate_lines(5)
        self.boardLines6 = self.generate_lines(6)


    def copy(self):
        b = GoBoard(self.size)
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.ko_recapture = self.ko_recapture
        b.last_move = self.last_move
        b.last2_move = self.last2_move
        b.current_player = self.current_player
        b.boardLines5 = self.boardLines5
        b.boardLines6 = self.boardLines6
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        return b

    def get_color(self, point):
        return self.board[point]

    def pt(self, row, col):
        return coord_to_point(row, col, self.size)

    def is_legal(self, point, color):
        """
        Check whether it is legal for color to play on point
        This method tries to play the move on a temporary copy of the board.
        This prevents the board from being modified by the move
        """
        board_copy = self.copy()
        can_play_move = board_copy.play_move(point, color)
        return can_play_move

    def get_empty_points(self):
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)

    def get_color_points(self, color):
        """
        Return:
            All points of color on the board
        """
        return where1d(self.board == color)

    def row_start(self, row):
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1

    def _initialize_empty_points(self, board):
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start = self.row_start(row)
            board[start : start + self.size] = EMPTY

    def play_move(self, point, color):
        """
        Play a move of color on point
        Returns boolean: whether move was legal
        """
        assert is_black_white(color)
        # Special cases
        if point == PASS:
            self.ko_recapture = None
            self.current_player = GoBoardUtil.opponent(color)
            self.last2_move = self.last_move
            self.last_move = point
            return True
        elif self.board[point] != EMPTY:
            return False
        self.board[point] = color
        self.current_player = GoBoardUtil.opponent(color)
        self.last2_move = self.last_move
        self.last_move = point
        return True

    def undo_move(self, move):
        self.board[move] = EMPTY
        self.current_player = GoBoardUtil.opponent(self.current_player)

    def last_board_moves(self):
        """
        Get the list of last_move and second last move.
        Only include moves on the board (not None, not PASS).
        """
        board_moves = []
        if self.last_move != None and self.last_move != PASS:
            board_moves.append(self.last_move)
        if self.last2_move != None and self.last2_move != PASS:
            board_moves.append(self.last2_move)
            return

    def detect_five_in_a_row(self):
        """
        Returns BLACK or WHITE if any five in a row is detected for the color
        EMPTY otherwise.
        """
        for r in self.rows:
            result = self.has_five_in_list(r)
            if result != EMPTY:
                return result
        for c in self.cols:
            result = self.has_five_in_list(c)
            if result != EMPTY:
                return result
        for d in self.diags:
            result = self.has_five_in_list(d)
            if result != EMPTY:
                return result
        return EMPTY

    def has_five_in_list(self, list):
        """
        Returns BLACK or WHITE if any five in a rows exist in the list.
        EMPTY otherwise.
        """
        prev = BORDER
        counter = 1
        for stone in list:
            if self.get_color(stone) == prev:
                counter += 1
            else:
                counter = 1
                prev = self.get_color(stone)
            if counter == 5 and prev != EMPTY:
                return prev
        return EMPTY

    # compute upon new board size
    def generate_lines(self, length):
        boardLines = []
        size = self.size
        for p in range(size * size):
            pointLines = \
                self.horizontal_lines(p, length) + \
                self.vertical_lines(p, length) + \
                self.diag_lines(p, size + 1, length) + \
                self.diag_lines(p, size - 1, length)
            boardLines.append(pointLines)
        return boardLines

    def horizontal_lines(self, pt, length):
        lines = []
        size = self.size
        start = max(pt - (length - 1), pt - (pt % size))
        end = min(pt + (length - 1), size * (pt // size + 1) - 1)

        for i in range(end - start - (length - 2)):
            lines.append(list(map(self.padded_point, range(start + i, start + i + length))))

        return lines

    def vertical_lines(self, pt, length):
        lines = []
        size = self.size    
        start = max(pt - ((length - 1) * size), pt % size)
        end = min(pt + ((length - 1) * size), (size - 1) * size + (pt % size))

        for i in range(start, end - ((length - 1) * size) + 1, size):
            lines.append(list(map(self.padded_point, range(i, i + ((length - 1) * size) + 1, size))))

        return lines

    def diag_lines(self, pt, dir, length):
        lines = []
        size = self.size
        row = pt // size
        col = pt % size

        if dir == size - 1:
            maxBackwardDist = min(row, size - col - 1, length - 1)
            maxForwardDist = min(size - row - 1, col, length - 1)
        else:
            maxBackwardDist = min(row, col, length - 1)
            maxForwardDist = min(size - row - 1, size - col - 1, length - 1)

        start = pt - maxBackwardDist * dir
        end = pt + maxForwardDist * dir

        for i in range(start, end - ((length - 1) * dir) + 1, dir):
            lines.append(list(map(self.padded_point, range(i, i + ((length - 1) * dir) + 1, dir))))

        return lines

    def padded_point(self, pt):
        # convert point in board to padded board point
        size = self.size
        row = (pt // size) + 1
        col = (pt % size) + 1
        return row * (size + 1) + col

    def unpadded_point(self, pt):
        size = self.size
        row = pt // (size + 1) - 1
        col = pt % (size + 1) - 1
        return row * size + col

    def check_win(self, move):
        newPoint = self.unpadded_point(move)
        lines = self.boardLines5[newPoint]
        for line in lines:
            b_count, w_count, e_count = self.get_counts(line)
            if b_count == 5:
                return BLACK
            elif w_count == 5:
                return WHITE

        return EMPTY

    def get_counts(self, line):
        b_count = 0
        w_count = 0
        e_count = 0

        for p in line:
            stone = self.board[p]
            if stone == BLACK:
                b_count += 1
            elif stone == WHITE:
                w_count += 1
            else:
                e_count += 1

        return b_count, w_count, e_count

    def __str__(self):
        twod = GoBoardUtil.get_twoD_board(self)
        twod_str = ['[' + ' '.join(row) + ']' for row in twod]
        return '\n'.join(twod_str)
