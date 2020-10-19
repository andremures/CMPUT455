
import collections
from board_util import BLACK, WHITE, EMPTY


SCORE_MAP = [0, 1, 2, 5, 15]


def calc_score(counts, color):
    if color == BLACK:
        my_count, opp_count, open_count = counts
    else:
        opp_count, my_count, open_count = counts

    # Is blocked
    if my_count >= 1 and opp_count >= 1:
        return 0

    return SCORE_MAP[my_count] - SCORE_MAP[opp_count]


def evaluate(board, color):
    score = 0
    lines = board.rows + board.cols + board.diags

    for line in lines:
        for counts in LineCountIterator(line):
            score += calc_score(counts, color)

    return score


class LineCountIterator:
    def __init__(self, line):
        self.line = line
        self.size = len(line)

    def __iter__(self):
        self.b_count = 0
        self.w_count = 0
        self.e_count = 0
        self.index = 0
        self.q = collections.deque()
        return self

    def __next__(self):
        if self.index >= self.size or self.size < 5:
            raise StopIteration

        if len(self.q) == 5:
            stone = self.q.popleft()
            self._add(stone, -1)

        while len(self.q) < 5:
            stone = self.line[self.index]
            self.q.append(stone)
            self._add(stone, 1)
            self.index += 1

        return self.b_count, self.w_count, self.e_count

    def _add(self, stone, val):
        if stone == BLACK:
            self.b_count += val
        elif stone == WHITE:
            self.w_count += val
        else:
            self.e_count += val
