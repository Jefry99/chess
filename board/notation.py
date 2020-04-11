lettere = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
diz = {'Q':0, 'R':1, 'B':2, 'N':3}

def return_notation(tipo, pos, to, game, gameboard, promotion=None):
    mossa = ''
    space = 24
    if tipo in 'Pp':
        if game.capture:
            mossa += lettere[pos[0]] + 'x'
        mossa += lettere[to[0]] + str(to[1]+1)
        if promotion != None:
            if promotion in 'Qq':
                tipo_pezzo = 'Q'
            elif promotion in 'Rr':
                tipo_pezzo = 'R'
            elif promotion in 'Bb':
                tipo_pezzo = 'B'
            elif promotion in 'Nn':
                tipo_pezzo = 'N'
            mossa += '=' + tipo_pezzo
            space -= 2
    elif tipo in 'Kk':
        if game.capture:
            mossa += 'K' + 'x' + lettere[to[0]] + str(to[1]+1)
        else:
            mossa += 'K' + lettere[to[0]] + str(to[1]+1)
    else:
        pezzi = game.count_piece(not game.player_turn)
        if tipo in 'Qq':
            tipo_pezzo = 'Q'
        elif tipo in 'Rr':
            tipo_pezzo = 'R'
        elif tipo in 'Bb':
            tipo_pezzo = 'B'
        elif tipo in 'Nn':
            tipo_pezzo = 'N'

        if pezzi[diz[tipo_pezzo]] == 1:
            if game.capture:
                mossa += tipo_pezzo + 'x' + lettere[to[0]] + str(to[1]+1)
            else:
                mossa += tipo_pezzo + lettere[to[0]] + str(to[1]+1)
        elif pezzi[diz[tipo_pezzo]] == 2:
            lista = game.check_same_peice(not game.player_turn, tipo_pezzo, gameboard, to)
            if lista[2] == 1 and lista[3] == 1:
                if lista[0] == 1:
                    if game.capture:
                        mossa += tipo_pezzo + str(7-pos[1]+1) + 'x' + lettere[to[0]] + str(to[1]+1)
                    else:
                        mossa += tipo_pezzo + str(7-pos[1]+1) + lettere[to[0]] + str(to[1]+1)
                elif lista[1] == 1:
                    if game.capture:
                        mossa += tipo_pezzo + lettere[pos[0]] + 'x' + lettere[to[0]] + str(to[1]+1)
                    else:
                        mossa += tipo_pezzo + lettere[pos[0]] + lettere[to[0]] + str(to[1]+1)
                else:
                    if game.capture:
                        mossa += tipo_pezzo + str(7-pos[1]+1) + 'x' + lettere[to[0]] + str(to[1]+1)
                    else:
                        mossa += tipo_pezzo + str(7-pos[1]+1) + lettere[to[0]] + str(to[1]+1)
            else:
                if game.capture:
                    mossa += tipo_pezzo + 'x' + lettere[to[0]] + str(to[1]+1)
                else:
                    mossa += tipo_pezzo + lettere[to[0]] + str(to[1]+1)
        elif pezzi[diz[tipo_pezzo]] > 2:
            if game.capture:
                mossa += tipo_pezzo + lettere[pos[0]] + str(7-pos[1]+1) + 'x' + lettere[to[0]] + str(to[1]+1)
            else:
                mossa += tipo_pezzo + lettere[pos[0]] + str(7-pos[1]+1) + lettere[to[0]] + str(to[1]+1)
        
    if game.check:
        if not game.is_game_alive:
            mossa += '#'
        else:
            mossa += '+'

    if game.capture:
        space -= 1
    if tipo == 'Q':
        space -= 1
    return mossa.center(space)

if __name__ == "__main__":
    pass