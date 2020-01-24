from pieces import Pawn, King, Queen, Bishop, Knight, Rook, En_passant
#WHITE = 0
#BLACK = 1
dizionario = {"A": 0, "a": 0, "B": 1, "b": 1, "C": 2, "c": 2, "D": 3, "d": 3, "E": 4, "e": 4, "F": 5, "f": 5, "G": 6, "g": 6, "H": 7, "h": 7}

class Game:
    def __init__(self):
        self.gameboard = {}
        self.player_turn = 0
        self.create_board()

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
    try:
        # qui bisogna modificare perchè accetti la notazione normale
        print('prima la casella corrente poi destinazione, es: a2 a4')
        a, b = input().split(sep=' ')
        if a[0] in dizionario and b[0] in dizionario and int(a[1]) in range(1,9) and int(b[1]) in range(1,9):
            a = (dizionario[a[0]], int(a[1])-1)
            b = (dizionario[b[0]], int(b[1])-1)
            return a, b
        print('Ricontrolla la merda che hai scritto')
        return((-1, -1), (-1, -1)) 
    except:
        print('Ricontrolla la merda che hai scritto')
        return((-1, -1), (-1, -1))

def check_promotion(target, pos):
    global game
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

def check_enpassant(pos, to):
    global game
    global en_passant
    if pos[1] == 1:
        if pos[1]+2 == to[1]:
            d = (pos[0], pos[1]+1)
            game.gameboard[d] = En_passant(0)
            en_passant.append(d)
    elif pos[1] == 6:
        if pos[1]-2 == to[1]:
            d = (pos[0], pos[1] - 1)
            game.gameboard[d] = En_passant(1)
            en_passant.append(d)

game = Game()
en_passant = []
def main():
    msg = ''
    while True:
        game.print_board()
        print(msg)
        msg = ''
        pos, to = double_input()
        target = game.gameboard[pos]
        
        if target:
            if target.get_color() != game.player_turn:
                msg = 'muovi le pedine del tuo colore dio porco'
                continue
            target.find_valid_moves(pos, game.gameboard)
            if target.is_valid(to):
                msg = 'mossa valida'
                game.gameboard[pos] = None
                game.gameboard[to] = target
                if len(en_passant) == 1:
                    if game.gameboard[en_passant[0]].get_type() == 'E' or game.gameboard[en_passant[0]].get_type() == 'e':
                        del game.gameboard[en_passant[0]]
                        game.gameboard[en_passant[0]] = None
                    en_passant.clear()
                if target.get_type() == 'P' or target.get_type() == 'p':
                    check_promotion(target, to)
                    check_enpassant(pos, to)
                if game.player_turn:
                    game.player_turn = 0
                else:
                    game.player_turn = 1
            else:
                msg = 'mossa non valida'
        else:
            msg = 'pedina non trovata'
            target = None

if __name__ == "__main__":
    main()
