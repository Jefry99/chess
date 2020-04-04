import tkinter as tk
from tkinter import Frame, Button, Label, Canvas
from game import Game
import time

matrice1 = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'], ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['-', '-', '-', '-', '-', '-', '-', '-'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]
pezzi = {'R':'WhiteRook', 'N':'WhiteKnight', 'B':'WhiteBishop', 'Q':'WhiteQueen', 'K':'WhiteKing', 'P':'WhitePawn', 'r':'BlackRook', 'n':'BlackKnight', 'b':'BlackBishop', 'q':'BlackQueen', 'k':'BlackKing', 'p':'BlackPawn'}
BACKGROUND = '#909090'

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
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                self.rimuovi()
                #CreateCanvasObject(self.canvas, self.image_name, 35+70*(quadro[0]), 35+70*(quadro[1]), self.scacchiera)
                #self.canvas.delete(self.image_obj)
                #del self
            elif var == 2:
                self.scacchiera.select_promotion()
                self.scacchiera.window.wait_window(self.scacchiera.frame6)
                self.scacchiera.game.after_promotion(self.scacchiera.promozione)
                self.scacchiera.put_piece(self.scacchiera.game.make_matrix())
                self.rimuovi()
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
        self.canvas = None
        self.label = True
        self.pezzi = []
        self.game = None
        self.home = None
        self.make_home()
        self.img = []
        self.promozione = None

    def after_selection(self, promotion):
        self.promozione = promotion
        print(self.promozione)
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
        self.window.geometry('770x760')
        self.window.title('Chess by Jefry and Layneeeee')
        self.window.configure(bg=BACKGROUND, padx=65, pady=30)
        self.window.resizable(False, False)
        self.frame2 = Frame(self.window, bg=BACKGROUND, padx=10, pady=10)
        self.frame3 = Frame(self.window, bg=BACKGROUND, padx=10)
        self.frame4 = Frame(self.window, bg=BACKGROUND, pady=25)
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
        Label(self.frame3, text='A', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=0, padx=16)
        Label(self.frame3, text='B', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=1, padx=16)
        Label(self.frame3, text='C', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=2, padx=16)
        Label(self.frame3, text='D', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=3, padx=16)
        Label(self.frame3, text='E', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=4, padx=16)
        Label(self.frame3, text='F', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=5, padx=16)
        Label(self.frame3, text='G', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=6, padx=16)
        Label(self.frame3, text='H', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=7, padx=16)
        Label(self.frame2, text='8', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=0, column=0, pady=8)
        Label(self.frame2, text='7', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=1, column=0, pady=8)
        Label(self.frame2, text='6', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=2, column=0, pady=8)
        Label(self.frame2, text='5', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=3, column=0, pady=8)
        Label(self.frame2, text='4', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=4, column=0, pady=8)
        Label(self.frame2, text='3', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=5, column=0, pady=8)
        Label(self.frame2, text='2', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=6, column=0, pady=8)
        Label(self.frame2, text='1', bg=BACKGROUND, font=('Helvetica', 40)).grid(row=7, column=0, pady=8)
        Button(self.frame4, text='RESET', font=('Helvetica', 20), command=self.reset_all, padx=20).grid(row=0, column=0)
        Frame(self.frame4, bg=BACKGROUND, width=100).grid(row=0, column=1)
        Button(self.frame4, text='UNDO', font=('Helvetica', 20), command=self.undo, padx=20).grid(row=0, column=2)

if __name__ == "__main__":
    Scacchiera().home.mainloop()