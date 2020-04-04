from pieces import Pawn, King, Queen, Bishop, Knight, Rook, En_passant
import copy
#WHITE = 0
#BLACK = 1
dizionario = {"A": 0, "a": 0, "B": 1, "b": 1, "C": 2, "c": 2, "D": 3, "d": 3, "E": 4, "e": 4, "F": 5, "f": 5, "G": 6, "g": 6, "H": 7, "h": 7}
check = False

class Game:
    
    def __init__(self):
        self.gameboard = {}
        self.player_turn = 0
        self.create_board()
        self.matrix = []
        self.make_matrix()
        self.color_check = None
        self.pos_w_K = ()
        self.pos_b_k = ()
        self.color_check = None
        self.pedine_bianche = []
        self.pedine_nere = []
        self.en_passant = []
        self.is_game_alive = True
        self.b_kingside_cast = True
        self.b_queenside_cast = True
        self.w_kingside_cast = True
        self.w_queenside_cast = True
        self.history = []
        self.history.append(copy.deepcopy(self.gameboard))
        self.num_move = 0

    def endgame(self):
        self.is_game_alive = False

    def undo(self):
        if self.num_move != 0:
            self.num_move -= 1
            self.gameboard = copy.deepcopy(self.history[self.num_move])
            if self.player_turn:
                self.player_turn = 0
            else:
                self.player_turn = 1
        
    def check_move(self, pos, to):
        if self.is_game_alive:
            try:
                target = self.gameboard[pos]
            except:
                return 0
            
            if target:
                if target.get_color() != self.player_turn:
                    print('Muovi le pedine del tuo colore dio porco')
                    return 0
                tipo = target.get_type()
                if tipo == 'K' or tipo == 'k':
                    if tipo == 'K':
                        if self.w_kingside_cast and to == (pos[0]+2,pos[1]):
                            if check_kingside_cast(target.get_color(), copy.deepcopy(self.gameboard), self):
                                self.w_kingside_cast = False
                                self.w_queenside_cast = False
                                self.gameboard[pos] = None
                                self.gameboard[to] = target
                                self.gameboard[(7,0)] = None
                                self.gameboard[(5,0)] = Rook(0)
                                if len(self.en_passant):
                                    if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                                        del self.gameboard[self.en_passant[0]]
                                        self.gameboard[self.en_passant[0]] = None
                                    self.en_passant.clear()
                                check = check_check(target.get_color(), self.gameboard, self)
                                if check:
                                    if not self.color_check:
                                        check_mate(self.pos_b_k, self, check)
                                    else:
                                        check_mate(self.pos_w_K, self, check)
                                if self.player_turn:
                                    self.player_turn = 0
                                else:
                                    self.player_turn = 1
                                self.num_move += 1
                                return 1
                            else:
                                print('Arrocco non possibile')
                                return 0
                        elif self.w_queenside_cast and to == (pos[0]-2,pos[1]):
                            if check_queenside_cast(target.get_color(), copy.deepcopy(self.gameboard), self):
                                self.w_kingside_cast = False
                                self.w_queenside_cast = False
                                self.gameboard[pos] = None
                                self.gameboard[to] = target
                                self.gameboard[(0,0)] = None
                                self.gameboard[(3,0)] = Rook(0)
                                if len(self.en_passant):
                                    if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                                        del self.gameboard[self.en_passant[0]]
                                        self.gameboard[self.en_passant[0]] = None
                                    self.en_passant.clear()
                                check = check_check(target.get_color(), self.gameboard, self)
                                if check:
                                    if not self.color_check:
                                        check_mate(self.pos_b_k, self, check)
                                    else:
                                        check_mate(self.pos_w_K, self, check)
                                if self.player_turn:
                                    self.player_turn = 0
                                else:
                                    self.player_turn = 1
                                self.num_move += 1
                                return 1
                            else:
                                print('Arrocco non possibile')
                                return 0
                    else:
                        if self.b_kingside_cast and to == (pos[0]+2,pos[1]):
                            if check_kingside_cast(target.get_color(), copy.deepcopy(self.gameboard), self):
                                self.w_kingside_cast = False
                                self.w_queenside_cast = False
                                self.gameboard[pos] = None
                                self.gameboard[to] = target
                                self.gameboard[(7,7)] = None
                                self.gameboard[(5,7)] = Rook(1)
                                if len(self.en_passant):
                                    if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                                        del self.gameboard[self.en_passant[0]]
                                        self.gameboard[self.en_passant[0]] = None
                                    self.en_passant.clear()
                                check = check_check(target.get_color(), self.gameboard, self)
                                if check:
                                    if not self.color_check:
                                        check_mate(self.pos_b_k, self, check)
                                    else:
                                        check_mate(self.pos_w_K, self, check)
                                if self.player_turn:
                                    self.player_turn = 0
                                else:
                                    self.player_turn = 1
                                self.num_move += 1
                                return 1
                            else:
                                print('Arrocco non possibile')
                                return 0
                        elif self.b_queenside_cast and to == (pos[0]-2,pos[1]):
                            if check_queenside_cast(target.get_color(), copy.deepcopy(self.gameboard), self):
                                self.w_kingside_cast = False
                                self.w_queenside_cast = False
                                self.gameboard[pos] = None
                                self.gameboard[to] = target
                                self.gameboard[(0,7)] = None
                                self.gameboard[(3,7)] = Rook(1)
                                if len(self.en_passant):
                                    if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                                        del self.gameboard[self.en_passant[0]]
                                        self.gameboard[self.en_passant[0]] = None
                                    self.en_passant.clear()
                                check = check_check(target.get_color(), self.gameboard, self)
                                if check:
                                    if not self.color_check:
                                        check_mate(self.pos_b_k, self, check)
                                    else:
                                        check_mate(self.pos_w_K, self, check)
                                if self.player_turn:
                                    self.player_turn = 0
                                else:
                                    self.player_turn = 1
                                self.num_move += 1
                                return 1
                            else:
                                print('Arrocco non possibile')
                                return 0

                target.find_valid_moves(pos, self.gameboard)
                if target.is_valid(to):
                    mod_gameboard = copy.deepcopy(self.gameboard)
                    del mod_gameboard[pos]
                    mod_gameboard[pos] = None
                    mod_gameboard[to] = target
                    if len(self.en_passant) and (tipo == 'P' or tipo == 'p'):
                        if tipo == 'P':
                            del mod_gameboard[(to[0], to[1]-1)]
                            mod_gameboard[(to[0], to[1]-1)] = None
                        else:
                            del mod_gameboard[(to[0], to[1]+1)]
                            mod_gameboard[(to[0], to[1]+1)] = None
                    if not check_check((not target.get_color()), mod_gameboard, self):
                        print('Mossa valida')
                        self.gameboard[pos] = None
                        self.gameboard[to] = target
                        if len(self.en_passant):
                            if tipo == 'P' or tipo == 'p':
                                if not target.get_color():
                                    del mod_gameboard[(to[0], to[1]-1)]
                                    self.gameboard[(to[0], to[1]-1)] = None
                                else:
                                    del mod_gameboard[(to[0], to[1]+1)]
                                    self.gameboard[(to[0], to[1]+1)] = None
                            if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                                del self.gameboard[self.en_passant[0]]
                                self.gameboard[self.en_passant[0]] = None
                            self.en_passant.clear()
                        if tipo == 'P' or tipo == 'p':
                            check_promotion(target, to, self)
                            check_enpassant(pos, to, self)
                        elif tipo == 'R':
                            if pos == (0,0):
                                self.w_queenside_cast = False
                            elif pos == (7,0):
                                self.w_kingside_cast = False
                        elif tipo == 'r':
                            if pos == (0,7):
                                self.b_queenside_cast = False
                            elif pos == (7,7):
                                self.b_kingside_cast = False
                        elif tipo == 'K':
                            self.w_kingside_cast = self.w_queenside_cast = False
                        elif tipo == 'k':
                            self.b_kingside_cast = self.b_queenside_cast = False
                        
                        check = check_check(target.get_color(), self.gameboard, self)
                        if check:
                            if not self.color_check:
                                check_mate(self.pos_b_k, self, check)
                            else:
                                check_mate(self.pos_w_K, self, check)
                        if self.player_turn:
                            self.player_turn = 0
                        else:
                            self.player_turn = 1
                        self.num_move += 1
                        try:
                            self.history[self.num_move]
                            self.history[self.num_move] = copy.deepcopy(self.gameboard)
                        except:
                            self.history.append(copy.deepcopy(self.gameboard))
                        return 1
                    else:
                        print('Non puoi farti scacco da solo')
                        return 0
                else:
                    print('Mossa non valida')
                    return 0            
        else:
            print('Game ended')
            return 0

    def make_matrix(self):
        self.matrix.clear()
        for i in range(8):
            self.matrix.append([])
        for i in range(8).__reversed__():
            for j in range(8):
                if (piece := self.gameboard[j, i]) is not None:
                    if piece.get_type() != 'E' and piece.get_type() != 'e':
                        self.matrix[i].append(piece.get_type())
                    else:
                        self.matrix[i].append('-')
                else:
                    self.matrix[i].append('-')
        return self.matrix

    def create_board(self):
        for i in range(8):
            self.gameboard[(i, 1)] = Pawn(0)
            self.gameboard[(i, 6)] = Pawn(1)

        placers = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for i in range(8):
            self.gameboard[(i, 0)] = placers[i](0)
        placers.reverse()
        for i in range(8):
            self.gameboard[((7-i), 7)] = placers[i](1)

        for i in range(8):
            for j in range(8):
                if j not in (0, 1, 6, 7):
                    self.gameboard[(i, j)] = None

    def print_board(self):
        print('\n')
        for i in range(8).__reversed__():
            x = ''
            for j in range(8):
                if (piece := self.gameboard[j, i]) is not None:
                    x += ' ' + piece.get_type() + ' '
                else:
                    x += ' - '
            x += '   ' + str(i+1)
            print(x)
        print('\n')
        print(' A  B  C  D  E  F  G  H')
        print('\n')


def double_input() -> ((int, int), (int, int)):
    print('prima la casella corrente poi destinazione, es: a2 a4')
    a = input()
    try:
        if a[0] == 'q':
            exit()
    except:
        exit()
    try:
        # qui bisogna modificare perchè accetti la notazione normale
        a, b = a.split(sep=' ')
        if a[0] in dizionario and b[0] in dizionario and int(a[1]) in range(1,9) and int(b[1]) in range(1,9):
            a = (dizionario[a[0]], int(a[1])-1)
            b = (dizionario[b[0]], int(b[1])-1)
            return a, b
        print('Ricontrolla la merda che hai scritto')
        return((-1, -1), (-1, -1)) 
    except:
        print('Ricontrolla la merda che hai scritto')
        return((-1, -1), (-1, -1))

def check_promotion(target, pos, game):
    if target.get_type() == 'P' and pos[1] == 7:
        promotion = input("Choose promotion(Q R K B): ")
        if promotion == 'Q':
            game.gameboard[pos] = Queen(0)
        elif promotion == 'R':
            game.gameboard[pos] = Rook(0)
        elif promotion == 'K':
            game.gameboard[pos] = Knight(0)
        elif promotion == 'B':
            game.gameboard[pos] = Bishop(0)
    elif target.get_type() == 'p' and pos[1] == 0:
        promotion = input("Choose promotion(q r k b): ")
        if promotion == 'q':
            game.gameboard[pos] = Queen(1)
        elif promotion == 'r':
            game.gameboard[pos] = Rook(1)
        elif promotion == 'k':
            game.gameboard[pos] = Knight(1)
        elif promotion == 'b':
            game.gameboard[pos] = Bishop(1)

def check_enpassant(pos, to, game):
    if pos[1] == 1:
        if pos[1]+2 == to[1]:
            d = (pos[0], pos[1]+1)
            game.gameboard[d] = En_passant(0)
            game.en_passant.append(d)
    elif pos[1] == 6:
        if pos[1]-2 == to[1]:
            d = (pos[0], pos[1] - 1)
            game.gameboard[d] = En_passant(1)
            game.en_passant.append(d)

def print_scacchiera(gameboard):
    print('\n')
    for i in range(8).__reversed__():
        x = ''
        for j in range(8):
            if (piece := gameboard[j, i]) is not None:
                x += ' ' + piece.get_type() + ' '
            else:
                x += ' - '
        x += '   ' + str(i+1)
        print(x)
    print('\n')
    print(' A  B  C  D  E  F  G  H')
    print('\n')

def check_mate(pos, game, check):
    mate = []
    mod_gameboard = None
    pedine_nere = []
    pedine_bianche = []
    for i in range(8):
        for j in range(8):
            if (piece := game.gameboard[(i,j)]) is not None:
                if not piece.get_color():
                    pedine_bianche.append(((i,j),piece))
                    if piece.get_type() == 'K':
                        game.pos_w_K = (i,j)
                else:
                    pedine_nere.append(((i,j),piece))
                    if piece.get_type() == 'k':
                        game.pos_b_k = (i,j)
    if not game.color_check:
        for piece in pedine_nere:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            for mossa in piece[1].avaiable_moves:
                print(mossa)
                del mod_gameboard
                mod_gameboard = copy.deepcopy(game.gameboard)
                del mod_gameboard[piece[0]]
                mod_gameboard[mossa] = copy.deepcopy(piece[1])
                mod_gameboard[piece[0]] = None
                check1 = False
                if check_check(game.color_check, mod_gameboard, game):
                    check1 = True
                print(check1)
                if not check1:
                    break
            if check1:
                mate.append(1)
            else:
                mate.append(0)
    else:
        for piece in pedine_bianche:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            for mossa in piece[1].avaiable_moves:
                del mod_gameboard
                mod_gameboard = copy.deepcopy(game.gameboard)
                del mod_gameboard[piece[0]]
                mod_gameboard[mossa] = piece[1]
                mod_gameboard[piece[0]] = None
                check1 = False
                if check_check(game.color_check, mod_gameboard, game):
                    check1 = True
                if check1:
                    break
            if not check1:
                mate.append(1)
            else:
                mate.append(0)
    print(mate)
    if 0 not in mate:
        print('CHECKMATE')
        game.endgame()

def check_check(color, gameboard, game):
    game.pedine_bianche.clear()
    game.pedine_nere.clear()
    pos_not_avaiable = []
    for i in range(8):
        for j in range(8):
            if (piece := gameboard[(i,j)]) is not None:
                if not piece.get_color():
                    game.pedine_bianche.append(((i,j),piece))
                    if piece.get_type() == 'K':
                        game.pos_w_K = (i,j)
                else:
                    game.pedine_nere.append(((i,j),piece))
                    if piece.get_type() == 'k':
                        game.pos_b_k = (i,j)
    if not color:
        for piece in game.pedine_bianche:
            piece[1].get_take_moves(piece[0], gameboard)
            pos_not_avaiable = piece[1].can_take
            if game.pos_b_k in pos_not_avaiable:
                game.color_check = color
                check = True
                return True
    else:
        for piece in game.pedine_nere:
            piece[1].get_take_moves(piece[0], gameboard)
            pos_not_avaiable = piece[1].can_take
            if game.pos_w_K in pos_not_avaiable:
                game.color_check = color
                check = True
                return True
    return False

def check_kingside_cast(color, gameboard, game):
    if not color:
        if gameboard[(5,0)] == None and gameboard[(6,0)] == None:
            gameboard[(4,0)] = None
            gameboard[(5,0)] = King(0)
            if not check_check(not color, gameboard, game):
                gameboard[(5,0)] = None
                gameboard[(6,0)] = King(0)
                if not check_check(not color, gameboard, game):
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        if gameboard[(5,7)] == None and gameboard[(6,7)] == None:
            gameboard[(4,7)] = None
            gameboard[(5,7)] = King(1)
            if not check_check(not color, gameboard, game):
                gameboard[(5,7)] = None
                gameboard[(6,7)] = King(1)
                if not check_check(not color, gameboard, game):
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0

def check_queenside_cast(color, gameboard, game):
    if not color:
        if gameboard[(3,0)] == None and gameboard[(2,0)] == None:
            gameboard[(4,0)] = None
            gameboard[(3,0)] = King(0)
            if not check_check(not color, gameboard, game):
                gameboard[(3,0)] = None
                gameboard[(2,0)] = King(0)
                if not check_check(not color, gameboard, game):
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        if gameboard[(3,7)] == None and gameboard[(2,7)] == None:
            gameboard[(4,7)] = None
            gameboard[(3,7)] = King(1)
            if not check_check(not color, gameboard, game):
                gameboard[(3,7)] = None
                gameboard[(2,7)] = King(1)
                if not check_check(not color, gameboard, game):
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0

def main():
    game = Game()
    while True:
        game.print_board()
        pos, to = double_input()
        game.check_move(pos, to)

if __name__ == "__main__":
    main()
