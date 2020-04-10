import tkinter as tk
from tkinter import *
from game import Game
from collections import defaultdict
import sys
import time
import csv

matrice1 = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'], ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]
pezzi = {'R':'WhiteRook', 'N':'WhiteKnight', 'B':'WhiteBishop', 'Q':'WhiteQueen', 'K':'WhiteKing', 'P':'WhitePawn', 'r':'BlackRook', 'n':'BlackKnight', 'b':'BlackBishop', 'q':'BlackQueen', 'k':'BlackKing', 'p':'BlackPawn'}
BACKGROUND = '#909090'

class Timer(object):
    def __init__(self, time, increase, color, label, scacchiera):
        self.scacchiera = scacchiera
        self.home = scacchiera.home
        self.min = time
        self.sec = 0
        self.color = color
        self.run = False
        self.increase = increase
        self.label = label
        self.label['text'] = str(self.min) + ':' + '{0:0=2d}'.format(self.sec)

    def start(self):
        if self.run:
            if self.sec == 0:
                if self.min == 0:
                    self.lose()
                else:
                    self.sec = 60
                    self.min -= 1
            self.sec -= 0.5
            self.label['text'] = str(self.min) + ':' + '{0:0=2d}'.format(int(self.sec))
            self.home.after(500, self.start)
    
    def lose(self):
        self.scacchiera.running_timer.run = False
        self.scacchiera.game.endgame()
        self.scacchiera.update_scores(not self.color)

    def reset(self):
        self.min = 20
        self.sec = 0
        self.label['text'] = str(self.min) + ':' + '{0:0=2d}'.format(int(self.sec))

class CreateCanvasObject(object):
    def __init__(self, canvas, image_name, xpos, ypos, scacchiera):
        self.canvas = canvas
        self.scacchiera = scacchiera
        self.image_name = image_name
        self.xpos, self.ypos = xpos, ypos
        self.start_x, self.start_y = xpos, ypos
        self.pos = None
        self.to = None
        self.tk_image = tk.PhotoImage(file="{}".format(image_name))
        self.image_obj= canvas.create_image(xpos, ypos, image=self.tk_image)
        canvas.tag_bind(self.image_obj, '<ButtonPress-1>', self.start)
        canvas.tag_bind(self.image_obj, '<Button1-Motion>', self.move)
        canvas.tag_bind(self.image_obj, '<ButtonRelease-1>', self.release)
        self.move_flag = False

    def rimuovi(self):
        self.canvas.delete(self.image_obj)
        del self

    def start(self, event):
        self.pos = (int(event.x/70), 7-int(event.y/70))
        self.start_x = int(event.x/70)
        self.start_y = int(event.y/70)

    def move(self, event):
        if not self.move_flag:
            self.move_flag = True
            self.canvas.tag_raise(self.image_obj)
            self.mouse_xpos = event.x
            self.mouse_ypos = event.y
        else:
            new_xpos, new_ypos = event.x, event.y
            self.canvas.move(self.image_obj,new_xpos-self.mouse_xpos ,new_ypos-self.mouse_ypos)
            self.mouse_xpos = new_xpos
            self.mouse_ypos = new_ypos
 
    def release(self, event):
        self.move_flag = False
        if event.x > 0 and event.y > 0 and event.x < 556 and event.y < 556:
            self.to = (int(event.x/70), 7-int(event.y/70))
            if (var := self.scacchiera.game.check_move(self.pos, self.to)) == 1:
                self.scacchiera.flip_timer()
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                self.scacchiera.running_timer.start()
                self.rimuovi()
                #CreateCanvasObject(self.canvas, self.image_name, 35+70*(quadro[0]), 35+70*(quadro[1]), self.scacchiera)
                #self.canvas.delete(self.image_obj)
                #del self
            elif var == 2:
                self.scacchiera.flip_timer()
                self.scacchiera.select_promotion()
                self.scacchiera.window.wait_window(self.scacchiera.frame6)
                self.scacchiera.game.after_promotion(self.scacchiera.promozione)
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                a = CreateCanvasObject(self.canvas, 'png/{}.png'.format(pezzi[self.scacchiera.promozione]), 35+70*self.to[0], 35+70*(7-self.to[1]), self.scacchiera)
                self.scacchiera.pezzi.append(a)
                self.scacchiera.running_timer.start()
                self.rimuovi()
            elif str(var) in '456':
                self.scacchiera.running_timer.run = False
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                self.rimuovi()
                self.scacchiera.disable_buttons()
                if var == 4:
                    print('Vince il bianco')
                    self.scacchiera.update_scores(0)
                elif var == 5:
                    print('Vince il nero')
                    self.scacchiera.update_scores(1)
                else:
                    print('Patta')
                    self.scacchiera.update_scores(3)
            else:
                a = CreateCanvasObject(self.canvas, self.image_name, 35+70*self.start_x, 35+70*self.start_y, self.scacchiera)
                self.scacchiera.pezzi.append(a)
                self.rimuovi()
            #self.canvas.itemconfig(self.canvas.find_withtag('ciao0', fill='blue')
            #print(self.canvas.find_withtag('ciao{}'.format(quadro)))
            #print(self.canvas.coords(self.canvas.find_withtag('ciao1')))
        else:
            a = CreateCanvasObject(self.canvas, self.image_name, 35+70*self.start_x, 35+70*self.start_y, self.scacchiera)
            self.scacchiera.pezzi.append(a)
            self.rimuovi()

class Scacchiera(Frame):
    def __init__(self):
        self.window = None
        self.frame2 = None
        self.frame3 = None
        self.frame4 = None
        self.frame5 = None
        self.frame6 = None
        self.frame7 = None
        self.canvas = None
        self.label = True
        self.pezzi = []
        self.game = None
        self.home = None
        self.img = []
        self.promozione = None
        self.tileSize = 70
        self.white_timer = None
        self.black_timer = None
        self.running_timer = None
        self.stall_offer = None
        self.give_up_color = None
        self.undo_request_color = None
        self.button = []
        self.score_board = None
        self.score_cells = []
        self.n_partite = None
        self.make_home()

    def disable_buttons(self):
        for but in self.button[:6]:
            but['state'] = 'disabled'
        self.button[6].grid_forget()

    def cancel_undo_request(self):
        self.button[6].grid_forget()
        self.undo_request_color = None
        for button in self.button:
            button['state'] = 'normal'

    def cancel_stall_offer(self):
        for but in self.button[:6]:
            but['state'] = 'normal'
        self.stall_offer = None
        self.button[6].grid_forget()

    def cancel_give_up(self):
        for but in self.button[:6]:
            but['state'] = 'normal'
        self.give_up_color = None
        self.button[6].grid_forget()

    def undo_request(self, color):
        if self.undo_request_color == None:
            self.undo_request_color = color
            if not color:
                self.button[6]['anchor'] = 'n'
                self.button[6]['command'] = self.cancel_undo_request
                self.button[6].grid(row=2, column=6)
                self.button[5]['state'] = 'disabled'
            else:
                self.button[6]['anchor'] = 's'
                self.button[6]['command'] = self.cancel_undo_request
                self.button[6].grid(row=0, column=6, pady=(60,0))
                self.button[4]['state'] = 'disabled'
            self.button[1]['state'] = 'disabled'
            self.button[3]['state'] = 'disabled'
            self.button[0]['state'] = 'disabled'
            self.button[2]['state'] = 'disabled'
        else:
            self.undo()
            self.button[6].grid_forget()
            self.undo_request_color = None
            for button in self.button:
                button['state'] = 'normal'

    def give_up(self, color):
        if self.give_up_color == None:
            self.give_up_color = color
            if not color:
                self.button[6]['anchor'] = 'n'
                self.button[6]['command'] = self.cancel_give_up
                self.button[6].grid(row=2, column=6)
                self.button[0]['state'] = 'disabled'
                self.button[1]['state'] = 'disabled'
                self.button[2]['state'] = 'disabled'
                self.button[4]['state'] = 'disabled'
                self.button[5]['state'] = 'disabled'
            else:
                self.button[6]['anchor'] = 's'
                self.button[6]['command'] = self.cancel_give_up
                self.button[6].grid(row=0, column=6, pady=(60,0))
                self.button[0]['state'] = 'disabled'
                self.button[2]['state'] = 'disabled'
                self.button[3]['state'] = 'disabled'
                self.button[4]['state'] = 'disabled'
                self.button[5]['state'] = 'disabled'
        elif self.give_up_color == color:
            self.running_timer.run = False
            self.game.endgame()
            self.disable_buttons()
            self.update_scores(not color)

    def stall(self, color, button):
        if self.stall_offer == None:
            self.stall_offer = color
            button['state'] = 'disabled'
            if not color:
                self.button[6]['anchor'] = 'n'
                self.button[6]['command'] = self.cancel_stall_offer
                self.button[6].grid(row=2, column=6)
            else:
                self.button[6]['anchor'] = 's'
                self.button[6]['command'] = self.cancel_stall_offer
                self.button[6].grid(row=0, column=6, pady=(60,0))
            self.button[1]['state'] = 'disabled'
            self.button[3]['state'] = 'disabled'
            self.button[4]['state'] = 'disabled'
            self.button[5]['state'] = 'disabled'
        else:
            self.running_timer.run = False
            self.game.stall()
            self.disable_buttons()
            self.update_scores(3)

    def flip_timer(self):
        if self.white_timer.run:
            self.white_timer.run = False
            self.black_timer.run = True
            self.running_timer = self.black_timer
        else:
            self.black_timer.run = False
            self.white_timer.run = True
            self.running_timer = self.white_timer

    def update_scores(self, score):
        with open('scores.txt', 'a') as f:
            if score == 0:
                f.write('\n1,0')
            elif score == 1:
                f.write('\n0,1')
            else:
                f.write('\n1/2,1/2')
        self.load_score()
    
    def somma(self, lista):
        ris = 0
        for elem in lista:
            if elem == '1/2':
                ris += 0.5
            else:
                ris += int(elem)
        return ris

    def load_score(self):
        columns = defaultdict(list)
        try:
            with open('scores.txt') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for (k,v) in row.items(): 
                        columns[k].append(v)
        except:
            f = open('scores.txt', 'w+')
            f.write('Player 1,Player 2')
            f.close()
            self.load_score()
            return
        if len(columns['Player 1']) > 12:
            columns['Player 1'] = columns['Player 1'][len(columns['Player 1'])-12:]
            columns['Player 2'] = columns['Player 2'][len(columns['Player 2'])-12:]
        else:
            while len(columns['Player 1']) != 12:
                columns['Player 1'].append(0)
                columns['Player 2'].append(0)
        i, k, j = 2, 14, 0
        while i < 14:
            self.score_cells[i]['text'] = columns['Player 1'][j]
            i += 1
            self.score_cells[k]['text'] = columns['Player 2'][j]
            k += 1
            j += 1
        self.score_cells[26]['text'] = self.somma(columns['Player 1'])
        self.score_cells[27]['text'] = self.somma(columns['Player 2'])

    def after_selection(self, promotion):
        self.promozione = promotion
        self.img = []
        self.canvas.config(state='normal')
        self.frame6.destroy()

    def select_promotion(self):
        self.canvas.config(state='disabled')
        self.frame6 = Frame(self.window, bg='white', height=90, width=420)
        self.frame6.grid(row=0, column=0)
        if not self.game.player_turn:
            self.img.append(tk.PhotoImage(file='png/WhiteQueen.png'))
            self.img.append(tk.PhotoImage(file='png/WhiteRook.png'))
            self.img.append(tk.PhotoImage(file='png/WhiteBishop.png'))
            self.img.append(tk.PhotoImage(file='png/WhiteKnight.png'))
            a = Label(self.frame6, image=self.img[0])
            a.grid(row=0, column=0)
            a.bind("<Button-1>", lambda e,x = 'Q': self.after_selection(x))
            b = Label(self.frame6, image=self.img[1])
            b.grid(row=0, column=1)
            b.bind("<Button-1>", lambda e,x = 'R': self.after_selection(x))
            c = Label(self.frame6, image=self.img[2])
            c.grid(row=0, column=2)
            c.bind("<Button-1>", lambda e,x = 'B': self.after_selection(x))
            d = Label(self.frame6, image=self.img[3])
            d.grid(row=0, column=3)
            d.bind("<Button-1>", lambda e,x = 'K': self.after_selection(x))
        else:
            self.img.append(tk.PhotoImage(file='png/BlackQueen.png'))
            self.img.append(tk.PhotoImage(file='png/BlackRook.png'))
            self.img.append(tk.PhotoImage(file='png/BlackBishop.png'))
            self.img.append(tk.PhotoImage(file='png/BlackKnight.png'))
            a = Label(self.frame6, image=self.img[0])
            a.grid(row=0, column=0)
            a.bind("<Button-1>", lambda e,x = 'q': self.after_selection(x))
            b = Label(self.frame6, image=self.img[1])
            b.grid(row=0, column=1)
            b.bind("<Button-1>", lambda e,x = 'r': self.after_selection(x))
            c = Label(self.frame6, image=self.img[2])
            c.grid(row=0, column=2)
            c.bind("<Button-1>", lambda e,x = 'b': self.after_selection(x))
            d = Label(self.frame6, image=self.img[3])
            d.grid(row=0, column=3)
            d.bind("<Button-1>", lambda e,x = 'k': self.after_selection(x))

    def staccah(self):
        self.home.quit()

    def coming_soon(self):
        if self.label: 
            Label(self.frame5, text='COMING SOON!', pady=30, bg=BACKGROUND, font=('Helvetica', 40)).grid(row=3, column=0)
            self.label = False

    def nuova_partita(self):
        self.make_scacchiera()
        self.home.withdraw()

    def make_mod(self):
        self.frame5.grid(row=0, column=0)
        self.home.grid_columnconfigure(0, weight=1)
        self.home.grid_rowconfigure(0, weight=1)
        Button(self.frame5, text='2 Player', font=('Helvetica', 20), command=self.nuova_partita, padx=20).grid(row=0, column=0)
        Frame(self.frame5, bg=BACKGROUND, height=100).grid(row=1, column=0)
        Button(self.frame5, text='Play vs AI', font=('Helvetica', 20), command=self.coming_soon, padx=20).grid(row=2, column=0)

    def make_home(self):
        self.home = tk.Tk()
        self.home.geometry('500x500')
        self.home.title('Chess by Jefry and Layneeeee')
        self.home.configure(bg=BACKGROUND)
        self.home.resizable(False, False)
        self.frame5 = Frame(self.home, bg=BACKGROUND)
        self.make_mod()

    def make_scacchiera(self):
        self.window = tk.Toplevel(self.home)
        self.window.protocol("WM_DELETE_WINDOW", self.staccah)
        self.window.geometry('1170x720')
        self.window.title('Chess by Jefry and Layneeeee')
        self.window.configure(bg = BACKGROUND, padx=65, pady=30)
        #self.window.resizable(False, False)
        self.frame2 = Frame(self.window, bg=BACKGROUND, padx=10, height = self.tileSize*8, width = 50)
        self.frame3 = Frame(self.window, bg = BACKGROUND, pady = 10, width = self.tileSize*8, height = 50)
        self.frame4 = Frame(self.window, bg=BACKGROUND, pady=25)
        self.frame7 = Frame(self.window, bg=BACKGROUND, padx=70)
        self.canvas = Canvas(self.window, width=556, height=556, bg='#edd9b9', highlightbackground="light grey")
        self.canvas.grid(row=0, column=0)
        self.make()
        self.game = Game()
        self.put_piece(self.game.make_matrix())

    def reset_all(self):
        del self.game
        self.game = Game()
        self.pulisci_scacchiera()
        self.pezzi.clear()
        self.put_piece(self.game.make_matrix())
        for button in self.button:
            button['state'] = 'normal'
        self.stall_offer = None
        self.give_up_color = None
        self.running_timer = self.black_timer
        self.white_timer.reset()
        self.black_timer.reset()
        self.black_timer.run = True
        print('Resetted')

    def undo(self):
        self.game.undo()
        self.pulisci_scacchiera()
        self.pezzi.clear()
        self.put_piece(self.game.make_matrix())
        print('Undo')

    def pulisci_scacchiera(self):
        for pezzo in self.pezzi:
            try:
                pezzo.rimuovi()
            except:
                pass

    def put_piece(self, matrix):
        self.pulisci_scacchiera()
        for i in range(8):
            for j in range(8):
                if (coso := matrix[i][7-j]) != '-':
                    path = 'png/' + pezzi[coso] + '.png'
                    a = CreateCanvasObject(self.canvas, path, 35+70*(7-j), 35+70*(7-i), self)
                    self.pezzi.append(a)
    
    def make(self):
        self.frame2.grid(row=0, column=1)
        self.frame3.grid(row=1, column=0)
        self.frame4.grid(row=2, column=0)
        self.frame7.grid(row=0, column=2, rowspan=2)
        cont = 0
        num = 0
        for n in range(1, 9):
            c = 0
            if n%2==0:
                for i in range(1, 9):
                    if c % 2 == 0:
                        self.canvas.create_rectangle(0+(i-1)*70, 0+(n-1)*70, 70+(i-1)*70, 70+(n-1)*70, fill='#edd9b9', outline='light grey', tags='ciao{}'.format(num))
                    else:
                        self.canvas.create_rectangle(0+(i-1)*70, 0+(n-1)*70, 70+(i-1)*70, 70+(n-1)*70, fill='#af8969', outline='light grey', tags='ciao{}'.format(num))
                    c += 1
                    num += 1
            else:
                for i in range(1, 9):
                    if c % 2 == 0:
                        self.canvas.create_rectangle(0+(i-1)*70, 0+(n-1)*70, 70+(i-1)*70, 70+(n-1)*70, fill='#af8969', outline='light grey', tags='ciao{}'.format(num))
                    else:
                        self.canvas.create_rectangle(0+(i-1)*70, 0+(n-1)*70, 70+(i-1)*70, 70+(n-1)*70, fill='#edd9b9', outline='light grey', tags='ciao{}'.format(num))
                    c += 1
                    num += 1
            cont += 1
        fontSize = 20
        self.frame2.pack_propagate(0)
        self.frame3.pack_propagate(0)
        l1 = Label(self.frame3, text='A', bg=BACKGROUND, font=('Helvetica', fontSize))
        l2 = Label(self.frame3, text='B', bg=BACKGROUND, font=('Helvetica', fontSize))
        l3 = Label(self.frame3, text='C', bg=BACKGROUND, font=('Helvetica', fontSize))
        l4 = Label(self.frame3, text='D', bg=BACKGROUND, font=('Helvetica', fontSize))
        l5 = Label(self.frame3, text='E', bg=BACKGROUND, font=('Helvetica', fontSize))
        l6 = Label(self.frame3, text='F', bg=BACKGROUND, font=('Helvetica', fontSize))
        l7 = Label(self.frame3, text='G', bg=BACKGROUND, font=('Helvetica', fontSize))
        l8 = Label(self.frame3, text='H', bg=BACKGROUND, font=('Helvetica', fontSize))
        l1.pack(side = LEFT, fill = BOTH, expand = True)
        l2.pack(side = LEFT, fill = BOTH, expand = True)
        l3.pack(side = LEFT, fill = BOTH, expand = True)
        l4.pack(side = LEFT, fill = BOTH, expand = True)
        l5.pack(side = LEFT, fill = BOTH, expand = True)
        l6.pack(side = LEFT, fill = BOTH, expand = True)
        l7.pack(side = LEFT, fill = BOTH, expand = True)
        l8.pack(side = LEFT, fill = BOTH, expand = True)
        h1 = Label(self.frame2, text='8', bg=BACKGROUND, font=('Helvetica', fontSize))
        h2 = Label(self.frame2, text='7', bg=BACKGROUND, font=('Helvetica', fontSize))
        h3 = Label(self.frame2, text='6', bg=BACKGROUND, font=('Helvetica', fontSize))
        h4 = Label(self.frame2, text='5', bg=BACKGROUND, font=('Helvetica', fontSize))
        h5 = Label(self.frame2, text='4', bg=BACKGROUND, font=('Helvetica', fontSize))
        h6 = Label(self.frame2, text='3', bg=BACKGROUND, font=('Helvetica', fontSize))
        h7 = Label(self.frame2, text='2', bg=BACKGROUND, font=('Helvetica', fontSize))
        h8 = Label(self.frame2, text='1', bg=BACKGROUND, font=('Helvetica', fontSize))
        h1.pack(fill = BOTH, expand = True)
        h2.pack(fill = BOTH, expand = True)
        h3.pack(fill = BOTH, expand = True)
        h4.pack(fill = BOTH, expand = True)
        h5.pack(fill = BOTH, expand = True)
        h6.pack(fill = BOTH, expand = True)
        h7.pack(fill = BOTH, expand = True)
        h8.pack(fill = BOTH, expand = True)
        Button(self.frame4, text='RESET', font=('Helvetica', 20), command=self.reset_all, padx=20).grid(row=0, column=0)
        Frame(self.frame4, bg=BACKGROUND, width=100).grid(row=0, column=1)
        Button(self.frame4, text='UNDO', font=('Helvetica', 20), command=self.undo, padx=20).grid(row=0, column=2)
        #frame7
        Label(self.frame7, text='Player 2', bg=BACKGROUND, font=('Helvetica', 20), width=10, anchor='w').grid(row=0, column=0, pady=(60,0))
        b_timer = Label(self.frame7, text='', font=('Helvetica', 20), bg=BACKGROUND)
        self.black_timer = Timer(20, 0, 1, b_timer, self)
        b_timer.grid(row=0, column=1, pady=(60,0))
        Frame(self.frame7, bg=BACKGROUND, width=60).grid(row=0, column=2, pady=(60,0))
        b1 = Button(self.frame7, text='1/2', font=('Helvetica', 20), bg=BACKGROUND, command=(lambda x=1: self.stall(x, b1)), width=2, height=1, highlightthickness = 0)
        b1.grid(row=0, column=4, pady=(60,0))
        b2 = Button(self.frame7, text='\u2690', font=('Helvetica', 20), bg=BACKGROUND, command=(lambda x=1: self.give_up(x)), width=2, height=1, highlightthickness = 0)
        b2.grid(row=0, column=5, pady=(60,0))
        Text(self.frame7, bg=BACKGROUND, font=('Helvetica', 20), width=30, height=10, pady=20).grid(row=1, column=0, columnspan=6)
        Label(self.frame7, text='Player 1', bg=BACKGROUND, font=('Helvetica', 20), width=10, anchor='w').grid(row=2, column=0)
        w_timer = Label(self.frame7, text='', font=('Helvetica', 20), bg=BACKGROUND)
        self.white_timer = Timer(20, 0, 0, w_timer, self)
        w_timer.grid(row=2, column=1)
        Frame(self.frame7, bg=BACKGROUND, width=60).grid(row=2, column=2)
        b3 = Button(self.frame7, text='1/2', font=('Helvetica', 20), bg=BACKGROUND, command=(lambda x=0: self.stall(x, b3)), width=2, height=1, highlightthickness = 0)
        b3.grid(row=2, column=4)
        b4 = Button(self.frame7, text='\u2690', font=('Helvetica', 20), bg=BACKGROUND, command=(lambda x=0: self.give_up(x)), width=2, height=1, highlightthickness = 0)
        b4.grid(row=2, column=5)
        b5 = Button(self.frame7, text='<-', font=('Helvetica', 20), bg=BACKGROUND, command=(lambda x=1: self.undo_request(x)), width=2, height=1, highlightthickness = 0)
        b5.grid(row=0, column=3, pady=(60,0))
        b6 = Button(self.frame7, text='<-', font=('Helvetica', 20), bg=BACKGROUND, command=(lambda x=0: self.undo_request(x)), width=2, height=1, highlightthickness = 0)
        b6.grid(row=2, column=3)
        b7 = Button(self.frame7, text='x', fg='red', font=('Helvetica', 18), bg=BACKGROUND, command=None, width=2, height=1, highlightthickness = 0)
        self.button.append(b1)
        self.button.append(b2)
        self.button.append(b3)
        self.button.append(b4)
        self.button.append(b5)
        self.button.append(b6)
        self.button.append(b7)
        self.running_timer = self.white_timer
        self.white_timer.run = True
        self.score_board = Frame(self.frame7, bg=BACKGROUND, pady=50)
        self.score_board.grid(row=3, column=0, columnspan=6)
        ll = Label(self.score_board, text="Player 1", bg=BACKGROUND, anchor='center', borderwidth=1, relief='raised')
        ll.grid(row=0, column=0)
        self.score_cells.append(ll)
        ll = Label(self.score_board, text="Player 2", bg=BACKGROUND, anchor='center', borderwidth=1, relief='raised')
        ll.grid(row=1, column=0)
        self.score_cells.append(ll)
        for i in range(2):
            for j in range(12):
                ll = Label(self.score_board, text="0", width=2, bg=BACKGROUND, anchor='center', borderwidth=1, relief='raised')
                ll.grid(row=i, column=j+1)
                self.score_cells.append(ll)
        ll = Label(self.score_board, text="", bg=BACKGROUND, width=3, anchor='center', borderwidth=1, relief='raised')
        ll.grid(row=0, column=13)
        self.score_cells.append(ll)
        ll = Label(self.score_board, text="", bg=BACKGROUND, width=3, anchor='center', borderwidth=1, relief='raised')
        ll.grid(row=1, column=13)
        self.score_cells.append(ll)
        self.load_score()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if str(sys.argv[1]) == '-d':
            a = Scacchiera()
            a.nuova_partita()
            a.home.mainloop()
        else:
            print('ma che cazzo di parametri metti?')
            exit()
    else:
        Scacchiera().home.mainloop()