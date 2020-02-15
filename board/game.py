from pieces import Pawn, King, Queen, Bishop, Knight, Rook, En_passant
import copy
#WHITE = 0
#BLACK = 1
dizionario = {"A": 0, "a": 0, "B": 1, "b": 1, "C": 2, "c": 2, "D": 3, "d": 3, "E": 4, "e": 4, "F": 5, "f": 5, "G": 6, "g": 6, "H": 7, "h": 7}

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
        self.pedine_bianche = []
        self.pedine_nere = []
        self.en_passant = []
        self.check = False
        
    def chech_move(self, pos, to):
        try:
            target = self.gameboard[pos]
        except:
            return 0
        
        if target:
            if target.get_color() != self.player_turn:
                print('Muovi le pedine del tuo colore dio porco')
                return 0

            target.find_valid_moves(pos, self.gameboard)
            if target.is_valid(to):
                mod_gameboard = copy.deepcopy(self.gameboard)
                del mod_gameboard[pos]
                mod_gameboard[pos] = None
                mod_gameboard[to] = target
                if len(self.en_passant) and (target.get_type() == 'P' or target.get_type() == 'p'):
                    if not target.get_color():
                        del mod_gameboard[(to[0], to[1]-1)]
                        mod_gameboard[(to[0], to[1]-1)] = None
                    else:
                        del mod_gameboard[(to[0], to[1]+1)]
                        mod_gameboard[(to[0], to[1]+1)] = None
                print_scacchiera(mod_gameboard)
                if not check_check((not target.get_color()), mod_gameboard, self):
                    print('Mossa valida')
                    self.gameboard[pos] = None
                    self.gameboard[to] = target
                    if len(self.en_passant) and (target.get_type() == 'P' or target.get_type() == 'p'):
                        if not target.get_color():
                            del mod_gameboard[(to[0], to[1]-1)]
                            self.gameboard[(to[0], to[1]-1)] = None
                        else:
                            del mod_gameboard[(to[0], to[1]+1)]
                            self.gameboard[(to[0], to[1]+1)] = None
                    if len(self.en_passant) == 1:
                        if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                            del self.gameboard[self.en_passant[0]]
                            self.gameboard[self.en_passant[0]] = None
                        self.en_passant.clear()
                    if target.get_type() == 'P' or target.get_type() == 'p':
                        check_promotion(target, to, self)
                        check_enpassant(pos, to, self)
                    check = check_check(target.get_color(), self.gameboard, self)
                    '''
                    if check:
                        if not self.color_check:
                            check_mate(self.pos_b_k, self.gameboard)
                        else:
                            check_mate(self.pos_w_K, self.gameboard)
                    '''
                    if self.player_turn:
                        self.player_turn = 0
                    else:
                        self.player_turn = 1
                    return 1
                else:
                    print('Non puoi farti scacco da solo')
                    return 0
            else:
                print('Mossa non valida')
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

def check_mate(pos, game):
    mod_gameboard = None
    if not game.color_check:
        for piece in game.pedine_nere:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            for mossa in piece[1].avaiable_moves:
                mod_gameboard = copy.deepcopy(game.gameboard)
                del mod_gameboard[piece[0]]
                mod_gameboard[mossa] = piece[1]
                mod_gameboard[piece[0]] = None
                for pezzo in game.pedine_bianche:
                    pezzo[1].get_take_moves(piece[0], mod_gameboard)
                    pos_not_avaiable = piece[1].can_take
                    if not (game.pos_b_k in pos_not_avaiable):
                        print(pos_not_avaiable)
                        print(game.pos_b_k)
                        print('dio bestia')
                        return
    else:
        for piece in game.pedine_bianche:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            for mossa in piece[1].avaiable_moves:
                mod_gameboard = copy.deepcopy(game.gameboard)
                del mod_gameboard[piece[0]]
                mod_gameboard[mossa] = piece[1]
                mod_gameboard[piece[0]] = None
                for pezzo in game.pedine_nere:
                    pezzo[1].get_take_moves(piece[0], mod_gameboard)
                    pos_not_avaiable = piece[1].can_take
                    if not (game.pos_w_K in pos_not_avaiable):
                        print('dio bestia')
                        return
    print('CHECKMATE')
    exit()

def check_check(color, gameboard, game):
    game.pedine_bianche.clear()
    game.pedine_nere.clear()
    pos_not_avaiable = []
    for i in range(8):
        for j in range(8):
            if (piece := gameboard[(i,j)]) is not None and gameboard[(i,j)].get_type() != 'e' and gameboard[(i,j)].get_type() != 'E':
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
                return True
    else:
        for piece in game.pedine_nere:
            piece[1].get_take_moves(piece[0], gameboard)
            pos_not_avaiable = piece[1].can_take
            if game.pos_w_K in pos_not_avaiable:
                game.color_check = color
                return True
    return False

def main():
    game = Game()
    while True:
        game.print_board()
        pos, to = double_input()
        game.chech_move(pos, to)

if __name__ == "__main__":
    main()
