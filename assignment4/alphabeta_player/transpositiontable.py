import random


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def store(self, code, result):
        # result is a tuple: (score, best_move)
        self.table[code] = result

    def lookup(self, code):
        return self.table.get(code)

    def returnTable(self):
        return self.table


class ZobristHasher:

    def __init__(self, boardSize):
        self.zobristArray = []
        self.boardIndices = boardSize*boardSize

        for _ in range(self.boardIndices):
            self.zobristArray.append([random.getrandbits(64) for _ in range(3)])
            # range 3 used as each piece on board needs 3 values for corresponding

    def hash(self, board):
        # board passed in has to be of the same size as boardSize*boardSize or it will probably crash
        # takes in board as a 1D array
        # board inputted would have a value 0 for a certain move (example empty), 1 for a certain move 
        # (example black), etc, as long as the numbering is consistent it will work.
        
        hashCode = self.zobristArray[0][board[0]]
        
        for i in range(1,self.boardIndices):
            hashCode = hashCode ^ self.zobristArray[i][board[i]]
        
        return hashCode



