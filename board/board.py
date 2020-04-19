import tkinter as tk
from tkinter import *
from game import *
import numpy as np
from notation import return_notation
from collections import defaultdict
import copy
import sys
import time
import csv
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from ai_non_nostra.config import Config
from ai_non_nostra.player_chess import ChessPlayer
from multiprocessing import Manager

# QUESTO E' IL CODICE MODIFICATO AL FINE DI INTRODURRE UNA AI DI CREAZIONE NON NOSTRA ALL'INTERNO DEL CODICE

matrice1 = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'], ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]
pezzi = {'R':'WhiteRook', 'N':'WhiteKnight', 'B':'WhiteBishop', 'Q':'WhiteQueen', 'K':'WhiteKing', 'P':'WhitePawn', 'r':'BlackRook', 'n':'BlackKnight', 'b':'BlackBishop', 'q':'BlackQueen', 'k':'BlackKing', 'p':'BlackPawn'}
BACKGROUND = '#909090'

class SelfPlayWorker:
    """
    Worker which trains a chess model using self play data. ALl it does is do self play and then write the
    game data to file, to be trained on by the optimize worker.

    Attributes:
        :ivar Config config: config to use to configure this worker
        :ivar ChessModel current_model: model to use for self play
        :ivar Manager m: the manager to use to coordinate between other workers
        :ivar list(Connection) cur_pipes: pipes to send observations to and get back mode predictions.
        :ivar list((str,list(float))): list of all the moves. Each tuple has the observation in FEN format and
            then the list of prior probabilities for each action, given by the visit count of each of the states
            reached by the action (actions indexed according to how they are ordered in the uci move list).
    """
    def __init__(self, config: Config):
        self.config = config
        self.current_model = self.load_model()
        self.m = Manager()
        self.cur_pipes = self.m.list(self.current_model.get_pipes(16))
        #self.cur_pipes = self.m.list([self.current_model.get_pipes(self.config.play.search_threads) for _ in range(self.config.play.max_processes)])

    def load_model(self):
        """
        Load the current best model
        :return ChessModel: current best model
        """
        from ai_non_nostra.model_chess import ChessModel
        model = ChessModel(self.config)
        model.build()
        return model

class Worker:
    def __init__(self):
        sys.setrecursionlimit(10000)
        self.config = Config()
        self.model = SelfPlayWorker(self.config)

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
        self.scacchiera.game.endgame(self.color)
        self.scacchiera.update_scores(not self.color)
        self.scacchiera.rematch()

    def reset(self):
        self.min = 20
        self.sec = 0
        self.label['text'] = str(self.min) + ':' + '{0:0=2d}'.format(int(self.sec))

class DisplayMove(object):
    def __init__(self, canvas, image_name, xpos, ypos, scacchiera, pezzo=None):
        self.canvas = canvas
        self.scacchiera = scacchiera
        self.x, self.y = xpos, ypos
        self.pezzo = pezzo
        self.image_name = image_name
        self.tk_image = tk.PhotoImage(file="{}".format(image_name))
        self.image_obj= self.canvas.create_image(xpos, ypos, image=self.tk_image)
        canvas.tag_bind(self.image_obj, '<ButtonPress-1>', self.start1)

    def start1(self, event):
        if self.pezzo != None:
            self.pezzo.release(event)

    def rimuovi(self):
        self.canvas.delete(self.image_obj)
        del self

class CreateCanvasObject(object):
    def __init__(self, canvas, image_name, xpos, ypos, scacchiera, tipo, player):
        self.canvas = canvas
        self.scacchiera = scacchiera
        self.image_name = image_name
        self.xpos, self.ypos = xpos, ypos
        self.start_x, self.start_y = xpos, ypos
        self.pos = None
        self.to = None
        self.tipo = tipo
        self.player = player
        self.tk_image = tk.PhotoImage(file="{}".format(image_name))
        self.image_obj= canvas.create_image(xpos, ypos, image=self.tk_image)
        if self.player != 'ai':
            canvas.tag_bind(self.image_obj, '<ButtonPress-1>', self.start)
            canvas.tag_bind(self.image_obj, '<Button1-Motion>', self.move)
            canvas.tag_bind(self.image_obj, '<ButtonRelease-1>', self.release)
        self.move_flag = False

    def rimuovi(self):
        self.canvas.delete(self.image_obj)
        del self

    def start(self, event):
        self.scacchiera.delete_trackers()
        self.pos = (int(event.x/70), 7-int(event.y/70))
        self.start_x = int(event.x/70)
        self.start_y = int(event.y/70)
        self.scacchiera.put_trackers(self.start_x, 7-self.start_y, self)

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
            gameboard = copy.deepcopy(self.scacchiera.game.gameboard)
            self.to = (int(event.x/70), 7-int(event.y/70))
            var = self.scacchiera.game.check_move(self.pos, self.to)
            if var == 1:
                if self.scacchiera.num_mosse > 0:
                    self.scacchiera.flip_timer()
                try:
                    self.scacchiera.check_tracker.rimuovi()
                except:
                    pass
                if self.scacchiera.game.check:
                    if not self.scacchiera.game.color_check:
                        self.scacchiera.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.scacchiera.game.pos_b_k[0]), 35+70*(7-self.scacchiera.game.pos_b_k[1]), self)
                    else:
                        self.scacchiera.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.scacchiera.game.pos_w_K[0]), 35+70*(7-self.scacchiera.game.pos_w_K[1]), self)
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                self.scacchiera.running_timer.start()
                self.scacchiera.delete_trackers()
                if self.scacchiera.num_mosse % 2 == 0:
                    self.scacchiera.num_mosse_da_scrivere += 1
                    text = '\n  ' + str(self.scacchiera.num_mosse_da_scrivere) + '. '
                else:
                    text = ' | '
                self.scacchiera.num_mosse += 1
                text += return_notation(self.tipo, (self.start_x,self.start_y), self.to, self.scacchiera.game, gameboard)
                self.scacchiera.text_area['state'] = 'normal'
                self.scacchiera.text_area.insert(INSERT, text)
                self.scacchiera.text_area['state'] = 'disabled'
                '''
                fen = self.scacchiera.game.return_fen()
                print(fen)
                matrici = cnn_input(fen)
                for matrice in matrici:
                    print(matrice)
                    print()
                print(self.scacchiera.game.return_avaiable_moves(1))
                '''
                self.rimuovi()
                #CreateCanvasObject(self.canvas, self.image_name, 35+70*(quadro[0]), 35+70*(quadro[1]), self.scacchiera)
                #self.canvas.delete(self.image_obj)
                #del self
            elif var == 2:
                if self.scacchiera.num_mosse > 0:
                    self.scacchiera.flip_timer()
                try:
                    self.scacchiera.check_tracker.rimuovi()
                except:
                    pass
                self.scacchiera.select_promotion()
                self.scacchiera.window.wait_window(self.scacchiera.frame6)
                self.scacchiera.game.after_promotion(self.scacchiera.promozione)
                if self.scacchiera.game.check:
                    if not self.scacchiera.game.color_check:
                        self.scacchiera.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.scacchiera.game.pos_b_k[0]), 35+70*(7-self.scacchiera.game.pos_b_k[1]), self)
                    else:
                        self.scacchiera.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.scacchiera.game.pos_w_K[0]), 35+70*(7-self.scacchiera.game.pos_w_K[1]), self)
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                a = CreateCanvasObject(self.canvas, 'png/{}.png'.format(pezzi[self.scacchiera.promozione]), 35+70*self.to[0], 35+70*(7-self.to[1]), self.scacchiera, self.tipo, self.player)
                self.scacchiera.pezzi.append(a)
                self.scacchiera.running_timer.start()
                self.scacchiera.delete_trackers()
                if self.scacchiera.num_mosse % 2 == 0:
                    self.scacchiera.num_mosse_da_scrivere += 1
                    text = '\n  ' + str(self.scacchiera.num_mosse_da_scrivere) + '. '
                else:
                    text = ' | '
                self.scacchiera.num_mosse += 1
                text += return_notation(self.tipo, (self.start_x,self.start_y), self.to, self.scacchiera.game, gameboard, promotion=self.scacchiera.promozione)
                self.scacchiera.text_area['state'] = 'normal'
                self.scacchiera.text_area.insert(INSERT, text)
                self.scacchiera.text_area['state'] = 'disabled'
                self.rimuovi()
            elif str(var) in '456':
                self.scacchiera.running_timer.run = False
                try:
                    self.scacchiera.check_tracker.rimuovi()
                except:
                    pass
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                self.scacchiera.disable_buttons()
                if var == 4:
                    print('Vince il bianco')
                    self.scacchiera.update_scores(0)
                    self.scacchiera.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.scacchiera.game.pos_b_k[0]), 35+70*(7-self.scacchiera.game.pos_b_k[1]), self)
                elif var == 5:
                    print('Vince il nero')
                    self.scacchiera.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.scacchiera.game.pos_w_K[0]), 35+70*(7-self.scacchiera.game.pos_w_K[1]), self)
                    self.scacchiera.update_scores(1)
                else:
                    print('Patta')
                    self.scacchiera.update_scores(3)
                self.scacchiera.delete_trackers()
                if self.scacchiera.num_mosse % 2 == 0:
                    self.scacchiera.num_mosse_da_scrivere += 1
                    text = '\n  ' + str(self.scacchiera.num_mosse_da_scrivere) + '. '
                else:
                    text = ' | '
                self.scacchiera.num_mosse += 1
                text += return_notation(self.tipo, (self.start_x,self.start_y), self.to, self.scacchiera.game, gameboard)
                self.scacchiera.text_area['state'] = 'normal'
                self.scacchiera.text_area.insert(INSERT, text)
                self.scacchiera.text_area['state'] = 'disabled'
                self.scacchiera.rematch()
                self.rimuovi()
            else:
                a = CreateCanvasObject(self.canvas, self.image_name, 35+70*self.start_x, 35+70*self.start_y, self.scacchiera, self.tipo, self.player)
                self.scacchiera.pezzi.append(a)
                self.rimuovi()
            if self.scacchiera.worker != None:
                self.canvas.update()
                self.scacchiera.ai_move()
            #self.canvas.itemconfig(self.canvas.find_withtag('ciao0', fill='blue')
            #print(self.canvas.find_withtag('ciao{}'.format(quadro)))
            #print(self.canvas.coords(self.canvas.find_withtag('ciao1')))
        else:
            a = CreateCanvasObject(self.canvas, self.image_name, 35+70*self.start_x, 35+70*self.start_y, self.scacchiera, self.tipo, self.player)
            self.scacchiera.pezzi.append(a)
            self.rimuovi()
        print(self.scacchiera.game.return_avaiable_moves())

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
        self.rematch_button = None
        self.score_board = None
        self.score_cells = []
        self.n_partite = None
        self.trackers = []
        self.check_tracker = None
        self.developer_mode = False
        self.text_area = None
        self.num_mosse = 0
        self.num_mosse_da_scrivere = 0
        self.worker = None
        self.ai = None
        self.make_home()

    def rematch(self):
        self.rematch_button.grid(row=3, column=0, columnspan=6, pady=(30,0))

    def delete_trackers(self):
        for trackers in self.trackers:
            trackers.rimuovi()

    def put_trackers(self, x, y, pezzo):
        moves, tipo = self.game.return_target_moves(x,y)
        pezzo.tipo = tipo
        for move in moves:
            if move[1]:
                a = DisplayMove(self.canvas, 'png/Capture.png', 35+70*(move[0][0]), 35+70*(7-move[0][1]), self, pezzo)
            else:
                a = DisplayMove(self.canvas, 'png/AvaiableMove.png', 35+70*(move[0][0]), 35+70*(7-move[0][1]), self, pezzo)
            self.trackers.append(a)

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
            self.game.endgame(color)
            self.disable_buttons()
            self.update_scores(not color)
            self.rematch()

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
            self.rematch()

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
        self.make_scacchiera_mod()
        self.home.withdraw()

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
        self.window.geometry("{0}x{1}+0+0".format(self.window.winfo_screenwidth(), self.window.winfo_screenheight()))
        self.window.title('Chess by Jefry and Layneeeee')
        self.window.configure(bg = BACKGROUND, padx=(self.window.winfo_screenwidth()-1050)/2, pady=(self.window.winfo_screenheight()-700)/2)
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
        self.running_timer.run = False
        self.running_timer = self.white_timer
        self.white_timer.reset()
        self.black_timer.reset()
        self.num_mosse = 0
        self.delete_trackers()
        try:
            self.check_tracker.rimuovi()
        except:
            pass
        try:
            self.rematch_button.grid_forget()
        except:
            pass
        self.text_area['state'] = 'normal'
        self.text_area.delete('1.0', END)
        self.text_area['state'] = 'disabled'
        print('Resetted')

    def undo(self):
        self.game.undo()
        self.game.update_castling_priviliges()
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
                coso = matrix[i][7-j]
                if coso != '-':
                    path = 'png/' + pezzi[coso] + '.png'
                    if coso in 'RNBQKP':
                        a = CreateCanvasObject(self.canvas, path, 35+70*(7-j), 35+70*(7-i), self, coso, 'player')
                    else:
                        if self.worker != None:
                            a = CreateCanvasObject(self.canvas, path, 35+70*(7-j), 35+70*(7-i), self, coso, 'ai')
                        else:
                            a = CreateCanvasObject(self.canvas, path, 35+70*(7-j), 35+70*(7-i), self, coso, 'player')
                    self.pezzi.append(a)
    
    def make(self):
        self.frame2.grid(row=0, column=1)
        self.frame3.grid(row=1, column=0)
        if self.developer_mode:
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
        if self.developer_mode:
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
        self.text_area = Text(self.frame7, bg=BACKGROUND, state='disabled', font=('Helvetica', 20), width=30, height=10, pady=20)
        self.text_area.grid(row=1, column=0, columnspan=6)
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
        self.rematch_button = Button(self.frame7, text='REMATCH', font=('Helvetica', 20), bg=BACKGROUND, command=self.reset_all, width=9, height=1, highlightthickness = 0)
        self.button.append(b1)
        self.button.append(b2)
        self.button.append(b3)
        self.button.append(b4)
        self.button.append(b5)
        self.button.append(b6)
        self.button.append(b7)
        self.running_timer = self.white_timer
        self.score_board = Frame(self.frame7, bg=BACKGROUND, pady=50)
        self.score_board.grid(row=4, column=0, columnspan=6)
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

    # CODICE PROVVISORIO E COSTRUITO SOLO PER L'IMPLEMENTAZIONE DI UNA AI PROVVISORIA
    def make_scacchiera_mod(self):
        self.window = tk.Toplevel(self.home)
        self.window.protocol("WM_DELETE_WINDOW", self.staccah)
        self.window.geometry("{0}x{1}+0+0".format(self.window.winfo_screenwidth(), self.window.winfo_screenheight()))
        self.window.title('Chess by Jefry and Layneeeee')
        self.window.configure(bg = BACKGROUND, padx=(self.window.winfo_screenwidth()-1050)/2, pady=(self.window.winfo_screenheight()-700)/2)
        #self.window.resizable(False, False)
        self.frame2 = Frame(self.window, bg=BACKGROUND, padx=10, height = self.tileSize*8, width = 50)
        self.frame3 = Frame(self.window, bg = BACKGROUND, pady = 10, width = self.tileSize*8, height = 50)
        self.frame4 = Frame(self.window, bg=BACKGROUND, pady=25)
        self.frame7 = Frame(self.window, bg=BACKGROUND, padx=70)
        self.canvas = Canvas(self.window, width=556, height=556, bg='#edd9b9', highlightbackground="light grey")
        self.canvas.grid(row=0, column=0)
        self.make_for_ai()
        self.game = Game()
        self.put_piece(self.game.make_matrix())

    def make_for_ai(self):
        self.frame2.grid(row=0, column=1)
        self.frame3.grid(row=1, column=0)
        if self.developer_mode:
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
        if self.developer_mode:
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
        self.text_area = Text(self.frame7, bg=BACKGROUND, state='disabled', font=('Helvetica', 20), width=30, height=10, pady=20)
        self.text_area.grid(row=1, column=0, columnspan=6)
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
        self.rematch_button = Button(self.frame7, text='REMATCH', font=('Helvetica', 20), bg=BACKGROUND, command=self.reset_all, width=9, height=1, highlightthickness = 0)
        self.button.append(b1)
        self.button.append(b2)
        self.button.append(b3)
        self.button.append(b4)
        self.button.append(b5)
        self.button.append(b6)
        self.button.append(b7)
        self.running_timer = self.white_timer
        self.score_board = Frame(self.frame7, bg=BACKGROUND, pady=50)
        self.score_board.grid(row=4, column=0, columnspan=6)
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
        self.worker = Worker()
        self.ai = ChessPlayer(self.worker.config, pipes=self.worker.model.cur_pipes)

    def ai_move(self):
        if self.game.player_turn:
            mossa = self.ai.action(self.game)
            mossa = ai_move(mossa)
            self.game.check_move(mossa[0], mossa[1])
            self.put_piece(self.game.make_matrix())
            if self.num_mosse > 0:
                self.flip_timer()
            try:
                self.check_tracker.rimuovi()
            except:
                pass
            if self.game.check:
                if not self.game.color_check:
                    self.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.game.pos_b_k[0]), 35+70*(7-self.game.pos_b_k[1]), self)
                else:
                    self.check_tracker = DisplayMove(self.canvas, 'png/Check.png', 35+70*(self.game.pos_w_K[0]), 35+70*(7-self.game.pos_w_K[1]), self)
            self.put_piece(self.game.make_matrix())
            self.running_timer.start()
            self.delete_trackers()
            if self.num_mosse % 2 == 0:
                self.num_mosse_da_scrivere += 1
                text = '\n  ' + str(self.num_mosse_da_scrivere) + '. '
            else:
                text = ' | '
            self.num_mosse += 1
            text += return_notation(self.game.gameboard[mossa[1]].get_type(), mossa[0], mossa[1], self.game, self.game.gameboard)
            self.text_area['state'] = 'normal'
            self.text_area.insert(INSERT, text)
            self.text_area['state'] = 'disabled'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if str(sys.argv[1]) == '-d':
            a = Scacchiera()
            a.developer_mode = True
            a.nuova_partita()
            a.home.mainloop()
        else:
            print('ma che cazzo di parametri metti?')
            exit()
    else:
        Scacchiera().home.mainloop()