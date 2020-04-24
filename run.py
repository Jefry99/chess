import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if str(sys.argv[1]) == 'self':
            from src.training.self_play import main
            main()
        elif str(sys.argv[1]) == 'opt':
            from src.training.optimize import main
            main()
        elif str(sys.argv[1]) == 'eval':
            from src.training.valuta import main
            main()
        else:
            print('ma che cazzo di parametri metti?')
            exit()
    else:
        from src.board.board import main
        main()