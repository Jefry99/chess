import tkinter as tk
from tkinter import Frame, Label, Canvas
from game import Game
import time

matrice1 = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'], ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]
pezzi = {'R':'WhiteRook', 'N':'WhiteKnight', 'B':'WhiteBishop', 'Q':'WhiteQueen', 'K':'WhiteKing', 'P':'WhitePawn', 'r':'BlackRook', 'n':'BlackKnight', 'b':'BlackBishop', 'q':'BlackQueen', 'k':'BlackKing', 'p':'BlackPawn'}

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
            if self.scacchiera.game.chech_move(self.pos, self.to):
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                self.canvas.delete(self.image_obj)
                del self
                #CreateCanvasObject(self.canvas, self.image_name, 35+70*(quadro[0]), 35+70*(quadro[1]), self.scacchiera)
                #self.canvas.delete(self.image_obj)
                #del self
            else:
                CreateCanvasObject(self.canvas, self.image_name, 35+70*self.start_x, 35+70*self.start_y, self.scacchiera)
                self.canvas.delete(self.image_obj)
                del self
            #self.canvas.itemconfig(self.canvas.find_withtag('ciao0', fill='blue')
            #print(self.canvas.find_withtag('ciao{}'.format(quadro)))
            #print(self.canvas.coords(self.canvas.find_withtag('ciao1')))
        else:
            CreateCanvasObject(self.canvas, self.image_name, 35+70*self.start_x, 35+70*self.start_y, self.scacchiera)
            self.canvas.delete(self.image_obj)
            del self

class Scacchiera(Frame):
    def __init__(self, matrice):
        self.window = tk.Tk()
        self.window.geometry('770x770')
        self.window.title('Chess by Jefry')
        self.window.configure(bg='grey', padx=70, pady=70)
        self.window.resizable(False, False)
        self.frame2 = Frame(self.window, bg='grey', padx=10, pady=10)
        self.frame3 = Frame(self.window, bg='grey', padx=10)
        self.canvas = Canvas(self.window, width=556, height=556, bg='#edd9b9', highlightbackground="light grey")
        self.canvas.grid(row=0, column=0)
        self.make()
        self.ready = False
        self.pezzi = []
        self.put_piece(matrice)
        self.game = Game()
    '''
    # switch state
    def switch_wait_state(self, event):
        self.wait_state = not self.wait_state
        print('Wait state switched to: %s ' % self.wait_state)

    # init events
    def init_events(self):
        self.bind('<Key>', self.wait)
        self.bind('<Control-s>', self.switch_wait_state)

    # waiter(listener) for keypress
    def wait(self, event):
        if self.wait_state and any(key == event.keysym for key in ['Left', 'Right']):
            print('I have successfully waited until %s keypress!' % event.keysym)
            self.do_smth(event.keysym)
        else:
            print('Wait state: %s , KeyPress: %s' % (self.wait_state, event.keysym))
            self.do_nhth()

    @staticmethod
    def do_smth(side):
        print("Don't be rude with me, Im trying my best on a %s side!" % side)

    @staticmethod
    def do_nhth():
        pass
    '''
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
        Label(self.frame3, text='A', bg='grey', font=('Helvetica', 40)).grid(row=0, column=0, padx=16)
        Label(self.frame3, text='B', bg='grey', font=('Helvetica', 40)).grid(row=0, column=1, padx=16)
        Label(self.frame3, text='C', bg='grey', font=('Helvetica', 40)).grid(row=0, column=2, padx=16)
        Label(self.frame3, text='D', bg='grey', font=('Helvetica', 40)).grid(row=0, column=3, padx=16)
        Label(self.frame3, text='E', bg='grey', font=('Helvetica', 40)).grid(row=0, column=4, padx=16)
        Label(self.frame3, text='F', bg='grey', font=('Helvetica', 40)).grid(row=0, column=5, padx=16)
        Label(self.frame3, text='G', bg='grey', font=('Helvetica', 40)).grid(row=0, column=6, padx=16)
        Label(self.frame3, text='H', bg='grey', font=('Helvetica', 40)).grid(row=0, column=7, padx=16)
        Label(self.frame2, text='8', bg='grey', font=('Helvetica', 40)).grid(row=0, column=0, pady=8)
        Label(self.frame2, text='7', bg='grey', font=('Helvetica', 40)).grid(row=1, column=0, pady=8)
        Label(self.frame2, text='6', bg='grey', font=('Helvetica', 40)).grid(row=2, column=0, pady=8)
        Label(self.frame2, text='5', bg='grey', font=('Helvetica', 40)).grid(row=3, column=0, pady=8)
        Label(self.frame2, text='4', bg='grey', font=('Helvetica', 40)).grid(row=4, column=0, pady=8)
        Label(self.frame2, text='3', bg='grey', font=('Helvetica', 40)).grid(row=5, column=0, pady=8)
        Label(self.frame2, text='2', bg='grey', font=('Helvetica', 40)).grid(row=6, column=0, pady=8)
        Label(self.frame2, text='1', bg='grey', font=('Helvetica', 40)).grid(row=7, column=0, pady=8)

if __name__ == "__main__":
    Scacchiera(matrice1).window.mainloop()