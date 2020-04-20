import numpy as np
import copy

class Pawn:
    def __init__(self, color):
        self.color = int(color)
        self.avaiable_moves = []
        self.can_take = []

    def get_take_moves(self, pos, board):
        self.can_take.clear()
        if not self.color:
            self.can_take.append((pos[0]+1,pos[1]+1))
            self.can_take.append((pos[0]-1,pos[1]+1))
        else:
            self.can_take.append((pos[0]+1,pos[1]-1))
            self.can_take.append((pos[0]-1,pos[1]-1))

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
        self.lista = []
        self.avaiable_moves = []
        self.can_take = []

    def get_take_moves(self, pos, board):
        self.can_take = [(pos[0]+1,pos[1]),(pos[0]-1,pos[1]),(pos[0],pos[1]+1),(pos[0],pos[1]-1),(pos[0]+1,pos[1]+1),(pos[0]-1,pos[1]-1),(pos[0]-1,pos[1]+1),(pos[0]+1,pos[1]-1)]

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        self.lista.clear()
        #up
        posx = pos[0]
        posy = pos[1] + 1
        if posy < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #down
        posx = pos[0]
        posy = pos[1] - 1
        if posy >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #right
        posx = pos[0] + 1
        posy = pos[1]
        if posx < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #left
        posx = pos[0] - 1
        posy = pos[1]
        if posx >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #up-right
        posx = pos[0] + 1
        posy = pos[1] + 1
        if posx < 8 and posy < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #up-left
        posx = pos[0] - 1
        posy = pos[1] + 1
        if posx >= 0 and posy < 8:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #down-left
        posx = pos[0] - 1
        posy = pos[1] - 1
        if posx >= 0 and posy >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #down-right
        posx = pos[0] + 1
        posy = pos[1] - 1
        if posx < 8 and posy >= 0:
            if board[(posx,posy)]:
                if board[(posx,posy)].get_color() != self.get_color():
                    self.lista.append((posx,posy))
            else:
                self.lista.append((posx,posy))
        #controllo se nelle posizioni disponibili sarebbe scacco
        for move in self.lista:
            mod_board = copy.copy(board)
            mod_board[move] = self
            del mod_board[pos]
            mod_board[pos] = None
            if not check_check((not self.get_color()), mod_board):
                self.avaiable_moves.append(move)

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
        self.can_take = []

    def get_take_moves(self, pos, board):
        self.can_take.clear()
        self.find_valid_moves(pos, board)
        self.can_take = self.avaiable_moves

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        #up-right
        posx = pos[0] + 1
        posy = pos[1] + 1
        while posx < 8 and posy < 8:
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
            if board[(pos[0],posizione)] and board[(pos[0],posizione)].get_type() not in 'Ee':
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
            if board[(pos[0],posizione)] and board[(pos[0],posizione)].get_type() not in 'Ee':
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
            if board[(posizione,pos[1])] and board[(posizione,pos[1])].get_type() not in 'Ee':
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
            if board[(posizione,pos[1])] and board[(posizione,pos[1])].get_type() not in 'Ee':
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
        self.can_take = []

    def get_take_moves(self, pos, board):
        self.can_take.clear()
        self.find_valid_moves(pos, board)
        self.can_take = self.avaiable_moves

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        #up-right
        posx = pos[0] + 1
        posy = pos[1] + 1
        while posx < 8 and posy < 8:
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
            if board[(posx,posy)] and board[(posx,posy)].get_type() not in 'Ee':
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
        self.can_take = []

    def get_take_moves(self, pos, board):
        self.can_take.clear()
        self.find_valid_moves(pos, board)
        self.can_take = self.avaiable_moves

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        knight_moves = [(pos[0]-1,pos[1]+2), (pos[0]+1,pos[1]+2), (pos[0]-1,pos[1]-2), (pos[0]+1,pos[1]-2), (pos[0]-2,pos[1]+1), (pos[0]-2,pos[1]-1), (pos[0]+2,pos[1]+1), (pos[0]+2,pos[1]-1)]
        for move in knight_moves:
            if not (((move[0] < 0) or (move[0] > 7)) or ((move[1] < 0) or (move[1] > 7))):
                if board[move]:
                    if board[move].get_color() != self.get_color():
                        self.avaiable_moves.append(move)
                else:
                    self.avaiable_moves.append(move)

    def is_valid(self, to):
        if to in self.avaiable_moves:
            return True
        return False

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return 'N'
        else:
            return 'n'

    def print(self):
        print('K')

class Rook:
    def __init__(self, color):
        self.color = color
        self.avaiable_moves = []
        self.can_take = []

    def get_take_moves(self, pos, board):
        self.can_take.clear()
        self.find_valid_moves(pos, board)
        self.can_take = self.avaiable_moves

    def find_valid_moves(self, pos, board):
        self.avaiable_moves.clear()
        #up
        posizione = pos[1] + 1
        while posizione < 8:
            if board[(pos[0],posizione)] and board[(pos[0],posizione)].get_type() not in 'Ee':
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
            if board[(pos[0],posizione)] and board[(pos[0],posizione)].get_type() not in 'Ee':
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
            if board[(posizione,pos[1])] and board[(posizione,pos[1])].get_type() not in 'Ee':
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
            if board[(posizione,pos[1])] and board[(posizione,pos[1])].get_type() not in 'Ee':
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
        self.avaiable_moves = []
        self.can_take = []

    def get_take_moves(self, pos, board):
        return None

    def find_valid_moves(self, pos, board):
        return None

    def get_color(self):
        return self.color

    def get_type(self):
        if not self.color:
            return 'E'
        else:
            return 'e'

    def print(self):
        print('e')

def check_check(color, gameboard):
    pedine_bianche = []
    pedine_nere = []
    pos_not_avaiable = []
    pos_w_K = ()
    pos_b_k = ()
    for i in range(8):
        for j in range(8):
            piece = gameboard[(i,j)]
            if piece is not None:
                if not piece.get_color():
                    pedine_bianche.append(((i,j),piece))
                    if piece.get_type() == 'K':
                        pos_w_K = (i,j)
                else:
                    pedine_nere.append(((i,j),piece))
                    if piece.get_type() == 'k':
                        pos_b_k = (i,j)
    if not color:
        for piece in pedine_bianche:
            piece[1].get_take_moves(piece[0], gameboard)
            pos_not_avaiable = piece[1].can_take
            if pos_b_k in pos_not_avaiable or pos_b_k in gameboard[pos_w_K].avaiable_moves:
                return True
    else:
        for piece in pedine_nere:
            piece[1].get_take_moves(piece[0], gameboard)
            pos_not_avaiable = piece[1].can_take
            if pos_w_K in pos_not_avaiable or pos_w_K in gameboard[pos_b_k].avaiable_moves:
                return True
    return False