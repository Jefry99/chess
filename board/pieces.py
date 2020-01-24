class Pawn:
    def __init__(self, color):
        self.color = int(color)
        self.avaiable_moves = []

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        if not self.color:
            d = (pos[0], pos[1]+1)
            if board[d] == None:
                self.avaiable_moves.append(d)
                d = (pos[0], pos[1]+2)
                if pos[1] == 1 and board[d] == None:
                    self.avaiable_moves.append(d)
            if pos[0] != 7:
                d = (pos[0]+1, pos[1]+1)
                if board[d] and board[d].get_color() != self.get_color():
                    self.avaiable_moves.append(d)
            d = (pos[0]-1, pos[1]+1)
            if pos[0] != 0:
                if board[d] and board[d].get_color() != self.get_color():
                    self.avaiable_moves.append(d)
        else:
            d = (pos[0], pos[1]-1)
            if board[d] == None:
                self.avaiable_moves.append(d)
                d = (pos[0], pos[1]-2)
                if pos[1] == 6 and board[d] == None:
                    self.avaiable_moves.append(d)
            if pos[0] != 7:
                d = (pos[0]+1, pos[1]-1)
                if board[d] and board[d].get_color() != self.get_color():
                    self.avaiable_moves.append(d)
            d = (pos[0]-1, pos[1]-1)
            if pos[0] != 0:
                if board[d] and board[d].get_color() != self.get_color():
                    self.avaiable_moves.append(d)

    def is_valid(self, to):
        if to in self.avaiable_moves:
            return True
        return False

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return 'P'
        else:
            return 'p'

    def print(self):
        print('p')

class King:
    def __init__(self, color):
        self.color = color
        self.avaiable_moves = []

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        #finire

    def is_valid(self, to):
        if to in self.avaiable_moves:
            return True
        return False

    def get_color(self):
        return self.color
    
    def get_type(self):
        if not self.color:
            return 'K'
        else:
            return 'k'

    def print(self):
        print('K')

class Queen:
    def __init__(self, color):
        self.color = color
        self.avaiable_moves = []

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        #up-right
        posx = pos[0] + 1
        posy = pos[1] + 1
        while posx < 8 and posy < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx += 1
            posy += 1
        #up-left
        posx = pos[0] - 1
        posy = pos[1] + 1
        while posx >= 0 and posy < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx -= 1
            posy += 1
        #down-left
        posx = pos[0] - 1
        posy = pos[1] - 1
        while posx >= 0 and posy >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx -= 1
            posy -= 1
        #down-right
        posx = pos[0] + 1
        posy = pos[1] - 1
        while posx < 8 and posy >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx += 1
            posy -= 1
        #up
        posizione = pos[1] + 1
        while posizione < 8:
            if board[(pos[0],posizione)]:
                if board[(pos[0],posizione)].get_color() != self.get_color():
                    self.avaiable_moves.append((pos[0],posizione))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((pos[0],posizione))
            posizione += 1
        #down
        posizione = pos[1] - 1
        while posizione >= 0:
            if board[(pos[0],posizione)]:
                if board[(pos[0],posizione)].get_color() != self.get_color():
                    self.avaiable_moves.append((pos[0],posizione))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((pos[0],posizione))
            posizione -= 1
        #right
        posizione = pos[0] + 1
        while posizione < 8:
            if board[(posizione,pos[1])]:
                if board[(posizione,pos[1])].get_color() != self.get_color():
                    self.avaiable_moves.append((posizione,pos[1]))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posizione,pos[1]))
            posizione += 1
        #left
        posizione = pos[0] - 1
        while posizione >= 0:
            if board[(posizione,pos[1])]:
                if board[(posizione,pos[1])].get_color() != self.get_color():
                    self.avaiable_moves.append((posizione,pos[1]))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posizione,pos[1]))
            posizione -= 1
    
    def is_valid(self, to):
        if to in self.avaiable_moves:
            return True
        return False

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return 'Q'
        else:
            return 'q'

    def print(self):
        print('Q')

class Bishop:
    def __init__(self, color):
        self.color = color
        self.avaiable_moves = []

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        #up-right
        posx = pos[0] + 1
        posy = pos[1] + 1
        while posx < 8 and posy < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx += 1
            posy += 1
        #up-left
        posx = pos[0] - 1
        posy = pos[1] + 1
        while posx >= 0 and posy < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx -= 1
            posy += 1
        #down-left
        posx = pos[0] - 1
        posy = pos[1] - 1
        while posx >= 0 and posy >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx -= 1
            posy -= 1
        #down-right
        posx = pos[0] + 1
        posy = pos[1] - 1
        while posx < 8 and posy >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.avaiable_moves.append((posx,posy))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posx,posy))
            posx += 1
            posy -= 1
    
    def is_valid(self, to):
        if to in self.avaiable_moves:
            return True
        return False

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return 'B'
        else:
            return 'b'

    def print(self):
        print('B')

class Knight:
    def __init__(self, color):
        self.color = color
        self.avaiable_moves = []

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        knight_moves = [(pos[0]-1,pos[1]+2), (pos[0]+1,pos[1]+2), (pos[0]-1,pos[1]-2), (pos[0]+1,pos[1]-2), (pos[0]-2,pos[1]+1), (pos[0]-2,pos[1]-1), (pos[0]+2,pos[1]+1), (pos[0]+2,pos[1]-1)]
        for move in knight_moves:
            if not (((move[0] < 0) or (move[0] > 7)) or ((move[1] < 0) or (move[1] > 7))):
                if board[move] and board[move].get_color() != self.get_color():
                    self.avaiable_moves.append(move)
                self.avaiable_moves.append(move)

    def is_valid(self, to):
        if to in self.avaiable_moves:
            return True
        return False

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return '@'
        else:
            return 'a'

    def print(self):
        print('K')

class Rook:
    def __init__(self, color):
        self.color = color
        self.avaiable_moves = []

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        #up
        posizione = pos[1] + 1
        while posizione < 8:
            if board[(pos[0],posizione)]:
                if board[(pos[0],posizione)].get_color() != self.get_color():
                    self.avaiable_moves.append((pos[0],posizione))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((pos[0],posizione))
            posizione += 1
        #down
        posizione = pos[1] - 1
        while posizione >= 0:
            if board[(pos[0],posizione)]:
                if board[(pos[0],posizione)].get_color() != self.get_color():
                    self.avaiable_moves.append((pos[0],posizione))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((pos[0],posizione))
            posizione -= 1
        #right
        posizione = pos[0] + 1
        while posizione < 8:
            if board[(posizione,pos[1])]:
                if board[(posizione,pos[1])].get_color() != self.get_color():
                    self.avaiable_moves.append((posizione,pos[1]))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posizione,pos[1]))
            posizione += 1
        #left
        posizione = pos[0] - 1
        while posizione >= 0:
            if board[(posizione,pos[1])]:
                if board[(posizione,pos[1])].get_color() != self.get_color():
                    self.avaiable_moves.append((posizione,pos[1]))
                    break
                else:
                    break
            else:
                self.avaiable_moves.append((posizione,pos[1]))
            posizione -= 1
    
    def is_valid(self, to):
        if to in self.avaiable_moves:
            return True
        return False

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return 'R'
        else:
            return 'r'     

    def print(self):
        print('R')

class En_passant:
    def __init__(self, color):
        self.color = int(color)

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return 'E'
        else:
            return 'e'

    def print(self):
        print('e')