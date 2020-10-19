import random;

class TranspositionTable:
    def __init__(self):
        self.table = {}


    def add(self, code, score):
        self.table[code] = score
        

    def get(self, code):
        return self.table.get(code)


class ZobristHasher:

    def __init__(self,boardSize):
        self.zobristArray = []
        self.boardIndices = boardSize*boardSize

        for _ in range(self.boardIndices):
            self.zobristArray.append([random.getrandbits(64) for _ in range(3)]) #range 3 used as each piece on board needs 3 values for corresponding 

    #probably never need to return it, just for testing, can remove if don't need it
    def returnZobristBoardArray(self):
        return self.zobristArray

    #following function also might be unnecassary, but created in case, we can remove
    #if boardSize changes (game will refresh, so old hash won't matter), 
    #need to make new zobristArray for corresponding size , we can also destroy old one and make a new one
    def newBoardSize(self,boardSize):
        self.boardIndices = boardSize
        self.zobristArray = []
        for _ in range(self.boardIndices):
            self.zobristArray.append([random.getrandbits(64) for _ in range(3)])


    #!!!the function we'll mostly be calling !!!!
    def createZobHash(self,board):
        # board passed in has to be of the same size as boardSize*boardSize or it will probably crash
        #takes in board as a 1D array
        # board inputted would have a value 0 for a certain move (example empty), 1 for a certain move 
        #(example black), etc, as long as the numbering is consistent it will work.

        if board[0] == 0:
            hashCode = self.zobristArray[0][0]
        elif board[0] == 1:
            hashCode = self.zobristArray[0][1]
        else:
            hashCode = self.zobristArray[0][2]
        
        for i in range(self.boardIndices):
            if board[i] == 0:
                hashCode = hashCode ^ self.zobristArray[i][0] 
                
            elif board[i] == 1:
                hashCode = hashCode ^ self.zobristArray[i][1]
            
            else:
                hashCode = hashCode ^ self.zobristArray[i][2]
        
        return hashCode


"""
# some code that runs hasher, initial call makes the zobrist array that is used for xor calls, otherwise
# just pass through a board, has to be a 1D of size boardSize*boardSize
# let me know if need to make changes !!!
hasher = ZobristHasher(2)
print(hasher.returnZobristBoardArray())
print(hasher.createZobHash([1,1,2,1]))
print(hasher.createZobHash([1,1,2,1]))
print(hasher.createZobHash([2,2,2,2]))
print(hasher.createZobHash([0,0,0,0]))
print(hasher.createZobHash([0,1,0,1]))
# different input causes unique values, as expected

hasher.newBoardSize(19)
print(hasher.returnZobristBoardArray())
newBoard = []

for i in range(19*19):
    newBoard.append(random.randint(0,2))

print(hasher.createZobHash(newBoard))

"""



    
