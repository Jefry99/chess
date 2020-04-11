lettere = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}

def return_notation(tipo, pos, to, game, gameboard, promotion=None):
    mossa = ''
    if tipo in 'Pp':
        if game.capture:
            mossa += lettere[pos[0]] + 'x'
        mossa += lettere[to[0]] + str(to[1]+1)
        if promotion != None:
            mossa += '=Q'
    elif tipo in 'Kk':
        if game.capture:
            mossa += 'K' + 'x' + lettere[to[0]] + str(to[1]+1)
        else:
            mossa += 'K' + lettere[to[0]] + str(to[1]+1)
    else:
        pezzi = game.count_piece(not game.player_turn)
        if tipo in 'Qq':
            if pezzi[0] == 1:
                if game.capture:
                    mossa += 'Q' + 'x' + lettere[to[0]] + str(to[1]+1)
                else:
                    mossa += 'Q' + lettere[to[0]] + str(to[1]+1)
            elif pezzi[0] == 2:
                lista = game.check_same_peice(not game.player_turn, 'Q', gameboard, to)
                if lista[2] == 1 and lista[3] == 1:
                    if lista[0] == 1:
                        if game.capture:
                            mossa += 'Q' + str(7-pos[1]+1) + 'x' + lettere[to[0]] + str(to[1]+1)
                        else:
                            mossa += 'Q' + str(7-pos[1]+1) + lettere[to[0]] + str(to[1]+1)
                    elif lista[1] == 1:
                        if game.capture:
                            mossa += 'Q' + lettere[pos[0]] + 'x' + lettere[to[0]] + str(to[1]+1)
                        else:
                            mossa += 'Q' + lettere[pos[0]] + lettere[to[0]] + str(to[1]+1)
                    else:
                        if game.capture:
                            mossa += 'Q' + str(7-pos[1]+1) + 'x' + lettere[to[0]] + str(to[1]+1)
                        else:
                            mossa += 'Q' + str(7-pos[1]+1) + lettere[to[0]] + str(to[1]+1)
                else:
                    if lista[0] == 1:
                        if game.capture:
                            mossa += 'Q' + str(7-pos[1]+1) + 'x' + lettere[to[0]] + str(to[1]+1)
                        else:
                            mossa += 'Q' + str(7-pos[1]+1) + lettere[to[0]] + str(to[1]+1)
                    elif lista[1] == 1:
                        if game.capture:
                            mossa += 'Q' + lettere[pos[0]] + 'x' + lettere[to[0]] + str(to[1]+1)
                        else:
                            mossa += 'Q' + lettere[pos[0]] + lettere[to[0]] + str(to[1]+1)
                    else:
                        if game.capture:
                            mossa += 'Q' + 'x' + lettere[to[0]] + str(to[1]+1)
                        else:
                            mossa += 'Q' + lettere[to[0]] + str(to[1]+1)
            elif pezzi[0] > 2:
                if game.capture:
                    mossa += 'Q' + lettere[pos[0]] + str(7-pos[1]+1) + 'x' + lettere[to[0]] + str(to[1]+1)
                else:
                    mossa += 'Q' + lettere[pos[0]] + str(7-pos[1]+1) + lettere[to[0]] + str(to[1]+1)
        
    if game.check:
        if not game.is_game_alive:
            mossa += '#'
        else:
            mossa += '+'
    return mossa

if __name__ == "__main__":
    pass