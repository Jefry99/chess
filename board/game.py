from pieces import Pawn, King, Queen, Bishop, Knight, Rook, En_passant
import copy
import numpy as np
#WHITE = 0
#BLACK = 1
dizionario = {"A": 0, "a": 0, "B": 1, "b": 1, "C": 2, "c": 2, "D": 3, "d": 3, "E": 4, "e": 4, "F": 5, "f": 5, "G": 6, "g": 6, "H": 7, "h": 7}
lettere = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
switcher = {
        'a': 0,
        'b': 1,
        'c': 2, 
        'd': 3,
        'e': 4,
        'f': 5,
        'g': 6,
        'h': 7
    }
pieces_order = 'KQRBNPkqrbnp' # 12x8x8
castling_order = 'KQkq'       # 4x8x8
# fifty-move-rule             # 1x8x8
# en en_passant               # 1x8x8

pezzi = {pieces_order[i]: i for i in range(12)}

class Winner:
    draw = -1
    white = 0
    black = 1

class Game:
    
    def __init__(self):
        self.gameboard = {}
        self.player_turn = 0
        self.create_board()
        self.matrix = []
        self.make_matrix()
        self.pos_of_promotion = None
        self.check = False
        self.capture = False
        self.draw_threefold_repetition = []
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
        self.fifty_move_draw = 0
        self.history = []
        self.history.append(copy.deepcopy(self.gameboard))
        self.castle_history = []
        self.num_move = 0
        self.winner = None

    def white_to_move(self):
        return self.player_turn == 0

    def done(self):
        return self.winner is not None

    def stall(self):
        self.is_game_alive = False
        self.winner = Winner.draw

    def endgame(self, color):
        self.is_game_alive = False
        if not color:
            self.winner = Winner.white
        else:
            self.winner = Winner.black

    def update_castling_priviliges(self):
        self.w_kingside_cast = self.gameboard[(0,8)]
        self.w_queenside_cast = self.gameboard[(0,9)]
        self.b_kingside_cast = self.gameboard[(0,10)]
        self.b_queenside_cast = self.gameboard[(0,11)]

    def undo(self):
        self.en_passant.clear()
        if self.num_move != 0:
            self.num_move -= 1
            self.gameboard = copy.deepcopy(self.history[self.num_move])
            if self.player_turn:
                self.player_turn = 0
            else:
                self.player_turn = 1
     

    def check_move(self, pos, to):
        if self.is_game_alive:
            #Salvo la possibilità di fare arrocco per entrambi i giocatori
            self.gameboard[(0,8)] = self.w_kingside_cast
            self.gameboard[(0,9)] = self.w_queenside_cast
            self.gameboard[(0,10)] = self.b_kingside_cast
            self.gameboard[(0,11)] = self.b_queenside_cast
            try:
                target = self.gameboard[pos]
            except:
                return 0

            if self.gameboard[to] != None:
                self.capture = True
            else:
                self.capture = False
            
            if target:
                if target.get_color() != self.player_turn:
                    print('Muovi le pedine del tuo colore dio porco')
                    return 0
                tipo = target.get_type()
                if ((tipo == 'K' or tipo == 'k') and (not self.check)):
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

                                self.draw_threefold_repetition.append(self.make_matrix())
                                self.fifty_move_draw += 1

                                self.check = check_check(target.get_color(), self.gameboard, self)
                                if self.check:
                                    if not self.color_check:
                                        if check_mate(self.pos_b_k, self, self.check):
                                            return 4
                                    else:
                                        if check_mate(self.pos_w_K, self, self.check):
                                            return 5
                                else:
                                    if check_stall(self.player_turn, self) or check_stall_insufficient_material(self) or check_stall_threefold_repetition(self):
                                        return 6
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
                                
                                self.draw_threefold_repetition.append(self.make_matrix)
                                self.fifty_move_draw += 1

                                self.check = check_check(target.get_color(), self.gameboard, self)
                                if self.check:
                                    if not self.color_check:
                                        if check_mate(self.pos_b_k, self, self.check):
                                            return 4
                                    else:
                                        if check_mate(self.pos_w_K, self, self.check):
                                            return 5
                                else:
                                    if check_stall(self.player_turn, self) or check_stall_insufficient_material(self) or check_stall_threefold_repetition(self):
                                        return 6
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
                                self.b_kingside_cast = False
                                self.b_queenside_cast = False
                                self.gameboard[pos] = None
                                self.gameboard[to] = target
                                self.gameboard[(7,7)] = None
                                self.gameboard[(5,7)] = Rook(1)
                                if len(self.en_passant):
                                    if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                                        del self.gameboard[self.en_passant[0]]
                                        self.gameboard[self.en_passant[0]] = None
                                    self.en_passant.clear()
                                
                                self.draw_threefold_repetition.append(self.make_matrix())
                                self.fifty_move_draw += 1

                                self.check = check_check(target.get_color(), self.gameboard, self)
                                if self.check:
                                    if not self.color_check:
                                        if check_mate(self.pos_b_k, self, self.check):
                                            return 4
                                    else:
                                        if check_mate(self.pos_w_K, self, self.check):
                                            return 5
                                else:
                                    if check_stall(self.player_turn, self) or check_stall_insufficient_material(self) or check_stall_threefold_repetition(self):
                                        return 6
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
                                self.b_kingside_cast = False
                                self.b_queenside_cast = False
                                self.gameboard[pos] = None
                                self.gameboard[to] = target
                                self.gameboard[(0,7)] = None
                                self.gameboard[(3,7)] = Rook(1)
                                if len(self.en_passant):
                                    if self.gameboard[self.en_passant[0]].get_type() == 'E' or self.gameboard[self.en_passant[0]].get_type() == 'e':
                                        del self.gameboard[self.en_passant[0]]
                                        self.gameboard[self.en_passant[0]] = None
                                    self.en_passant.clear()

                                self.draw_threefold_repetition.append(self.make_matrix)
                                self.fifty_move_draw += 1

                                self.check = check_check(target.get_color(), self.gameboard, self)
                                if self.check:
                                    if not self.color_check:
                                        if check_mate(self.pos_b_k, self, self.check):
                                            return 4
                                    else:
                                        if check_mate(self.pos_w_K, self, self.check):
                                            return 5
                                else:
                                    if check_stall(self.player_turn, self) or check_stall_insufficient_material(self) or check_stall_threefold_repetition(self):
                                        return 6
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
                            if ((self.gameboard[self.en_passant[0]].get_type() == 'E') or (self.gameboard[self.en_passant[0]].get_type() == 'e')):
                                del self.gameboard[self.en_passant[0]]
                                self.gameboard[self.en_passant[0]] = None
                            self.en_passant.clear()
                        if tipo == 'P' or tipo == 'p':
                            if check_promotion(target, to, self):
                                return 2
                            check_enpassant(pos, to, self)
                            self.draw_threefold_repetition.clear()
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

                        if self.capture:
                            self.draw_threefold_repetition.clear()
                            self.draw_threefold_repetition.append(copy.deepcopy(self.make_matrix()))
                        else:
                            self.draw_threefold_repetition.append(copy.deepcopy(self.make_matrix()))
                        
                        if not self.capture and tipo not in 'Pp':
                            self.fifty_move_draw += 1
                        else:
                            self.fifty_move_draw = 0

                        self.check = check_check(target.get_color(), self.gameboard, self)
                        if self.check:
                            if not self.color_check:
                                if check_mate(self.pos_b_k, self, self.check):
                                    return 4
                            else:
                                if check_mate(self.pos_w_K, self, self.check):
                                    return 5
                        else:
                            if check_stall(self.player_turn, self) or check_stall_insufficient_material(self) or check_stall_threefold_repetition(self):
                                return 6
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

    def after_promotion(self, tipo):
        if tipo == 'Q':
            self.gameboard[self.pos_of_promotion] = Queen(0)
        elif tipo == 'R':
            self.gameboard[self.pos_of_promotion] = Rook(0)
        elif tipo == 'K':
            self.gameboard[self.pos_of_promotion] = Knight(0)
        elif tipo == 'B':
            self.gameboard[self.pos_of_promotion] = Bishop(0)
        elif tipo == 'q':
            self.gameboard[self.pos_of_promotion] = Queen(1)
        elif tipo == 'r':
            self.gameboard[self.pos_of_promotion] = Rook(1)
        elif tipo == 'k':
            self.gameboard[self.pos_of_promotion] = Knight(1)
        elif tipo == 'b':
            self.gameboard[self.pos_of_promotion] = Bishop(1)

        self.draw_threefold_repetition.clear()
        self.draw_threefold_repetition.append(self.make_matrix())
        self.fifty_move_draw = 0

        self.check = check_check(self.player_turn, self.gameboard, self)
        if self.check:
            if not self.color_check:
                if check_mate(self.pos_b_k, self, self.check):
                    return 4
            else:
                if check_mate(self.pos_w_K, self, self.check):
                    return 5
        else:
            if check_stall(self.player_turn, self) or check_stall_insufficient_material(self):
                return 6
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

    def make_matrix(self):
        self.matrix.clear()
        for i in range(8):
            self.matrix.append([])
        for i in range(8).__reversed__():
            for j in range(8):
                piece = self.gameboard[j, i]
                if piece is not None:
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
                piece = self.gameboard[j, i]
                if piece is not None:
                    x += ' ' + piece.get_type() + ' '
                else:
                    x += ' - '
            x += '   ' + str(i+1)
            print(x)
        print('\n')
        print(' A  B  C  D  E  F  G  H')
        print('\n')

    def check_same_peice(self, color, tipo, gameboard, to):
        regine = []
        torri = []
        alfieri = []
        cavalli = []
        da_ritornare = []
        if not color:
            for i in range(8):
                for j in range(8):
                    piece = gameboard[(i,j)]
                    if piece is not None:
                        tipo1 = piece.get_type()
                        if tipo1 == 'Q':
                            regine.append(((i,j), piece))
                        elif tipo1 == 'R':
                            torri.append(((i,j), piece))
                        elif tipo1 == 'B':
                            alfieri.append(((i,j), piece))
                        elif tipo1 == 'N':
                            cavalli.append(((i,j), piece))
            if tipo == 'Q':
                if regine[0][0][0] == regine[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if regine[0][0][1] == regine[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                regine[0][1].find_valid_moves(regine[0][0], gameboard)
                if regine[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                regine[1][1].find_valid_moves(regine[1][0], gameboard)
                if regine[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
            elif tipo == 'R':
                if torri[0][0][0] == torri[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if torri[0][0][1] == torri[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                torri[0][1].find_valid_moves(torri[0][0], gameboard)
                if torri[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                torri[1][1].find_valid_moves(torri[1][0], gameboard)
                if torri[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
            elif tipo == 'B':
                if alfieri[0][0][0] == alfieri[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if alfieri[0][0][1] == alfieri[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                alfieri[0][1].find_valid_moves(alfieri[0][0], gameboard)
                if alfieri[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                alfieri[1][1].find_valid_moves(alfieri[1][0], gameboard)
                if alfieri[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
            elif tipo == 'N':
                if cavalli[0][0][0] == cavalli[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if cavalli[0][0][1] == cavalli[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                cavalli[0][1].find_valid_moves(cavalli[0][0], gameboard)
                if cavalli[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                cavalli[1][1].find_valid_moves(cavalli[1][0], gameboard)
                if cavalli[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
        else:
            for i in range(8):
                for j in range(8):
                    piece = gameboard[(i,j)]
                    if piece is not None:
                        tipo1 = piece.get_type()
                        if tipo1 == 'q':
                            regine.append(((i,j), piece))
                        elif tipo1 == 'r':
                            torri.append(((i,j), piece))
                        elif tipo1 == 'b':
                            alfieri.append(((i,j), piece))
                        elif tipo1 == 'n':
                            cavalli.append(((i,j), piece))
            if tipo == 'Q':
                if regine[0][0][0] == regine[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if regine[0][0][1] == regine[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                regine[0][1].find_valid_moves(regine[0][0], gameboard)
                if regine[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                regine[1][1].find_valid_moves(regine[1][0], gameboard)
                if regine[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
            elif tipo == 'R':
                if torri[0][0][0] == torri[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if torri[0][0][1] == torri[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                torri[0][1].find_valid_moves(torri[0][0], gameboard)
                if torri[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                torri[1][1].find_valid_moves(torri[1][0], gameboard)
                if torri[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
            elif tipo == 'B':
                if alfieri[0][0][0] == alfieri[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if alfieri[0][0][1] == alfieri[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                alfieri[0][1].find_valid_moves(alfieri[0][0], gameboard)
                if alfieri[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                alfieri[1][1].find_valid_moves(alfieri[1][0], gameboard)
                if alfieri[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
            elif tipo == 'N':
                if cavalli[0][0][0] == cavalli[1][0][0]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                if cavalli[0][0][1] == cavalli[1][0][1]:
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                cavalli[0][1].find_valid_moves(cavalli[0][0], gameboard)
                if cavalli[0][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
                cavalli[1][1].find_valid_moves(cavalli[1][0], gameboard)
                if cavalli[1][1].is_valid(to):
                    da_ritornare.append(1)
                else:
                    da_ritornare.append(0)
        return da_ritornare

    def count_piece(self, color):
        n_regine = 0
        n_alfieri = 0
        n_cavalli = 0
        n_torri = 0
        if not color:
            for i in range(8):
                for j in range(8):
                    piece = self.gameboard[(i,j)]
                    try:
                        tipo = str(piece.get_type())
                    except:
                        tipo = ''
                        pass
                    if tipo == 'Q':
                        n_regine += 1
                    elif tipo == 'R':
                        n_torri += 1
                    elif tipo == 'N':
                        n_cavalli += 1
                    elif tipo == 'B':
                        n_alfieri += 1
        else:
            for i in range(8):
                for j in range(8):
                    piece = self.gameboard[(i,j)]
                    try:
                        tipo = str(piece.get_type())
                    except:
                        tipo = ''
                        pass
                    if tipo == 'q':
                        n_regine += 1
                    elif tipo == 'r':
                        n_torri += 1
                    elif tipo == 'n':
                        n_cavalli += 1
                    elif tipo == 'b':
                        n_alfieri += 1
        return [n_regine, n_torri, n_alfieri, n_cavalli]

    def return_fen(self):
        fen = '/'
        row = []
        for i in reversed(range(8)):
            space = 0
            s = ''
            for j in range(8):
                if self.gameboard[(j,i)] is not None:
                    if self.gameboard[(j,i)].get_type() not in 'Ee':
                        if space != 0:
                            s += str(space)
                            space = 0
                        s += self.gameboard[(j,i)].get_type()
                    else:
                        space += 1
                else:
                    space += 1
            if space != 0:
                s += str(space)
            row.append(s)
        fen = fen.join(row) + ' '
        fen += 'b ' if self.player_turn else 'w '
        cast = ''
        if self.w_kingside_cast:
            cast += 'K'
        if self.w_queenside_cast:
            cast += 'Q'
        if self.b_kingside_cast:
            cast += 'k'
        if self.b_queenside_cast:
            cast += 'q'
        if cast == '':
            fen += '- '
        else:
            fen += cast + ' '
        if len(self.en_passant) == 0:
            fen += '- '
        else:
            fen += lettere[self.en_passant[0][0]] + str(self.en_passant[0][1] + 1) + ' '
        fen += str(self.fifty_move_draw) + ' '
        return fen

    def return_avaiable_moves(self, color=None):
        if color == None:
            color = self.player_turn
        da_ritornare = []
        pedine_nere = []
        pedine_bianche = []
        for i in range(8):
            for j in range(8):
                piece = self.gameboard[(i,j)]
                if piece is not None:
                    if not piece.get_color():
                        pedine_bianche.append(((i,j),piece))
                    else:
                        pedine_nere.append(((i,j),piece))
        if not color:
            for pezzo in pedine_bianche:
                pezzo[1].find_valid_moves(pezzo[0], self.gameboard)
                for mossa in pezzo[1].avaiable_moves:
                    mod_gameboard = copy.deepcopy(self.gameboard)
                    del mod_gameboard[pezzo[0]]
                    mod_gameboard[pezzo[0]] = None
                    mod_gameboard[mossa] = pezzo[1]
                    if not check_check((not pezzo[1].get_color()), mod_gameboard, self):
                        da_ritornare.append(lettere[pezzo[0][0]] + str(pezzo[0][1]+1) + lettere[mossa[0]] + str(mossa[1]+1))
        else:
            for pezzo in pedine_nere:
                pezzo[1].find_valid_moves(pezzo[0], self.gameboard)
                for mossa in pezzo[1].avaiable_moves:
                    mod_gameboard = copy.deepcopy(self.gameboard)
                    del mod_gameboard[pezzo[0]]
                    mod_gameboard[pezzo[0]] = None
                    mod_gameboard[mossa] = pezzo[1]
                    if not check_check((not pezzo[1].get_color()), mod_gameboard, self):
                        da_ritornare.append(lettere[pezzo[0][0]] + str(pezzo[0][1]+1) + lettere[mossa[0]] + str(mossa[1]+1))
        return da_ritornare

    def return_target_moves(self, x, y):
        da_ritornare = []
        pezzo = self.gameboard[(x,y)]
        tipo = pezzo.get_type()
        if pezzo.color == self.player_turn and self.is_game_alive:
            if not self.check:
                if pezzo.get_type() in 'Kk':
                    if pezzo.get_type() == 'K':
                        if check_kingside_cast(pezzo.get_color(), copy.deepcopy(self.gameboard), self) and self.w_kingside_cast:
                            da_ritornare.append(((6,0), 0))
                        if check_queenside_cast(pezzo.get_color(), copy.deepcopy(self.gameboard), self) and self.w_queenside_cast:
                            da_ritornare.append(((2,0), 0))
                    else:
                        if check_kingside_cast(pezzo.get_color(), copy.deepcopy(self.gameboard), self) and self.b_kingside_cast:
                            da_ritornare.append(((6,7), 0))
                        if check_queenside_cast(pezzo.get_color(), copy.deepcopy(self.gameboard), self) and self.b_queenside_cast:
                            da_ritornare.append(((2,7), 0))
                pezzo.find_valid_moves((x,y), self.gameboard)
                for mossa in pezzo.avaiable_moves:
                    if self.gameboard[mossa] == None:
                        da_ritornare.append((mossa, 0))
                    else:
                        da_ritornare.append((mossa, 1))
            else:
                for mossa in pezzo.avaiable_moves:
                    mod_gameboard = copy.deepcopy(self.gameboard)
                    del mod_gameboard[(x,y)]
                    mod_gameboard[(x,y)] = None
                    mod_gameboard[mossa] = pezzo
                    if not check_check((not pezzo.get_color()), mod_gameboard, self):
                        if self.gameboard[mossa] == None:
                            da_ritornare.append((mossa, 0))
                        else:
                            da_ritornare.append((mossa, 1))
        return da_ritornare, tipo

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
        game.pos_of_promotion = pos
        return 1
    elif target.get_type() == 'p' and pos[1] == 0:
        game.pos_of_promotion = pos
        return 1
    return 0

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
            piece = gameboard[j, i]
            if piece is not None:
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
    check1 = False
    for i in range(8):
        for j in range(8):
            piece = game.gameboard[(i,j)]
            if piece is not None:
                if not piece.get_color():
                    pedine_bianche.append(((i,j),piece))
                else:
                    pedine_nere.append(((i,j),piece))
    if not game.color_check:
        for piece in pedine_nere:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            if len(piece[1].avaiable_moves) == 0:
                continue
            for mossa in piece[1].avaiable_moves:
                del mod_gameboard
                mod_gameboard = copy.deepcopy(game.gameboard)
                del mod_gameboard[piece[0]]
                mod_gameboard[mossa] = copy.deepcopy(piece[1])
                mod_gameboard[piece[0]] = None
                check1 = False
                if check_check(game.color_check, mod_gameboard, game):
                    check1 = True
                if not check1:
                    break
            if check1:
                mate.append(1)
            else:
                mate.append(0)
    else:
        for piece in pedine_bianche:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            if len(piece[1].avaiable_moves) == 0:
                continue
            for mossa in piece[1].avaiable_moves:
                del mod_gameboard
                mod_gameboard = copy.deepcopy(game.gameboard)
                del mod_gameboard[piece[0]]
                mod_gameboard[mossa] = copy.deepcopy(piece[1])
                mod_gameboard[piece[0]] = None
                check1 = False
                if check_check(game.color_check, mod_gameboard, game):
                    check1 = True
                if check1:
                    break
            if check1:
                mate.append(1)
            else:
                mate.append(0)
    if 0 not in mate:
        print('CHECKMATE')
        game.endgame(game.color_check)
        return True

def check_check(color, gameboard, game):
    game.pedine_bianche.clear()
    game.pedine_nere.clear()
    pos_not_avaiable = []
    for i in range(8):
        for j in range(8):
            piece = gameboard[(i,j)]
            if piece is not None:
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

def check_stall(color, game):
    if not color:
        for piece in game.pedine_nere:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            if len(piece[1].avaiable_moves) > 0:
                return
    else:
        for piece in game.pedine_bianche:
            piece[1].find_valid_moves(piece[0], game.gameboard)
            if len(piece[1].avaiable_moves) > 0:
                return
    print('STALL')
    game.stall()
    return True

def check_stall_insufficient_material(game):
    if len(game.pedine_bianche) == 2:
        if len(game.pedine_nere) == 2:
            for pezzo_b in game.pedine_bianche:
                if pezzo_b[1].get_type() in 'NB':
                    for pezzo_n in game.pedine_nere:
                        if pezzo_n[1].get_type() in 'nb':
                            print('STALL')
                            game.stall
                            return True
    elif len(game.pedine_bianche) == 1 and len(game.pedine_nere) == 1:
        print('STALL')
        game.stall()
        return True
    elif len(game.pedine_bianche) == 1:
        if len(game.pedine_nere) == 2:
            for pezzo_n in game.pedine_nere:
                if pezzo_n[1].get_type() in 'nb':
                    print('STALL')
                    game.stall()
                    return True
    elif len(game.pedine_nere) == 1:
        if len(game.pedine_bianche) == 2:
            for pezzo_b in game.pedine_bianche:
                if pezzo_b[1].get_type() in 'NB':
                    print('STALL')
                    game.stall()
                    return True
    return False

def check_stall_threefold_repetition(game):
    for position1 in game.draw_threefold_repetition:
        a = 0
        for position2 in game.draw_threefold_repetition:
            b = False
            if np.array_equal([position1], [position2]):
                b = True
            else:
                b = False
            if b:
                a += 1
        if a == 3:
            print('STALL')
            game.stall()
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
        if gameboard[(3,0)] == None and gameboard[(2,0)] == None and gameboard[(1,0)] == None:
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
        if gameboard[(3,7)] == None and gameboard[(2,7)] == None and gameboard[(1,7)] == None:
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

def cnn_input(fen):
    fen = maybe_reverse_fen(fen, black_turn(fen))
    return input_cnn(fen) # 18x8x8 matrix

def black_turn(fen):
    return fen.split(" ")[1] == 'b'

def maybe_reverse_fen(fen, flip = False):
    if not flip:
        return fen
    foo = fen.split(' ')
    rows = foo[0].split('/')
    def swapcase(a):
        if a.isalpha():
            return a.lower() if a.isupper() else a.upper()
        return a
    def swapall(aa):
        return "".join([swapcase(a) for a in aa])
    return "/".join([swapall(row) for row in reversed(rows)]) \
        + " " + ('w' if foo[1] == 'b' else 'b') \
        + " " + "".join(sorted(swapall(foo[2]))) \
        + " " + foo[3] + " " + foo[4] + " " + foo[5]

def input_cnn(fen):
    matrici_pezzi = make_matrici_pezzi(fen)
    matrici_mosse_speciali = make_matrici_speciali(fen)
    matrici_input = np.vstack((matrici_pezzi, matrici_mosse_speciali))
    assert matrici_input.shape == (18, 8, 8)
    return matrici_input

def make_matrici_speciali(fen):
    foo = fen.split(' ')

    en_passant = np.zeros((8, 8), dtype=np.float32)
    if foo[3] != '-':
        eps = alg_to_coord(foo[3])
        en_passant[eps[0]][eps[1]] = 1

    fifty_move_count = int(foo[4])
    fifty_move = np.full((8, 8), fifty_move_count, dtype=np.float32)

    castling = foo[2]
    auxiliary_planes = [np.full((8, 8), int('K' in castling), dtype=np.float32),
                        np.full((8, 8), int('Q' in castling), dtype=np.float32),
                        np.full((8, 8), int('k' in castling), dtype=np.float32),
                        np.full((8, 8), int('q' in castling), dtype=np.float32),
                        fifty_move,
                        en_passant]

    ret = np.asarray(auxiliary_planes, dtype=np.float32)
    assert ret.shape == (6, 8, 8)
    return ret

def alg_to_coord(alg):
    rank = 8 - int(alg[1])        # 0-7
    file = ord(alg[0]) - ord('a') # 0-7
    return rank, file

def make_matrici_pezzi(fen):
    fen_board = replace_tags(fen)
    pieces_both = np.zeros(shape=(12, 8, 8), dtype=np.float32)
    for rank in range(8):
        for file in range(8):
            v = fen_board[rank * 8 + file]
            if v.isalpha():
                pieces_both[pezzi[v]][rank][file] = 1
    assert pieces_both.shape == (12, 8, 8)
    return pieces_both

def ai_move(move):
    try:
        col1 = move[0]
        row1 = move[1]
        col2 = move[2]
        row2 = move[3]
    except:
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(move)
    c1 = switcher.get(col1)
    c2 = switcher.get(col2)
    return((c1, int(row1)-1), (c2, int(row2)-1))

def replace_tags(board):
    board = board.split(" ")[0]
    board = board.replace("2", "11")
    board = board.replace("3", "111")
    board = board.replace("4", "1111")
    board = board.replace("5", "11111")
    board = board.replace("6", "111111")
    board = board.replace("7", "1111111")
    board = board.replace("8", "11111111")
    return board.replace("/", "")

def main():
    game = Game()
    while True:
        game.print_board()
        pos, to = double_input()
        #pos_ai, to_ai = ai_move("a2a4")
        game.check_move(pos, to)

if __name__ == "__main__":
    main()