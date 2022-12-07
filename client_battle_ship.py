import pygame as pg
from tkinter import Tk, Label, StringVar, Button, Entry
import socket
import json
import pprint
import threading


pg.init()

matrix = []
size = (800, 600)
screen = pg.display.set_mode(size)
ARIAL_30 = pg.font.SysFont('arial', 50)
COURIER = pg.font.SysFont('courier new', 24)
row_numbers = COURIER.render(' 1 2 3 4 5 6 7 8 9 10', True, (180, 0, 0))
BLACK = (0, 0, 0)


playing = False


def thread_to_listen(messages, player1):
    while True:
        if not messages:
            messages.append(player1.parse_server_message())


messages = []


class Player:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 12345))
        global matrix
        global playing
        print(f"connected")
        playing = True
        self.matrix = matrix
        self.enemy_saved_matrix = [["0" for _ in range(10)] for _ in range(10)]
        print(self.parse_server_message())
        self.send_to_server(json.dumps(self.matrix))


    def send_to_server(self, data):
        self.client.send(data.encode("utf-8"))

    def parse_server_message(self):
        data = self.client.recv(2048).decode("utf-8")
        return data

    def __repr__(self):
        return self.matrix, self.enemy_saved_matrix


class Menu:
    def __init__(self):
        self._options = []
        self._callbacks = []
        self._current_option_index = 0
        self._in_shadow = False

    def append_option(self, option, callback):
        self._options.append(ARIAL_30.render(option, True, (255, 255, 255)))
        self._callbacks.append(callback)

    def switch(self, direction):
        if not self._in_shadow:
            self._current_option_index = max(0, min(self._current_option_index + direction, len(self._options) - 1))

    def select(self):
        if not self._in_shadow:
            self._callbacks[self._current_option_index]()

    def selected(self):
        if not self._in_shadow:
            return self._current_option_index

    def draw(self, surf, x, y, option_y_padding):
        for i, option in enumerate(self._options):
            option_rect: pg.Rect = option.get_rect()
            option_rect.topleft = (x, y + i * option_y_padding)
            if i == self._current_option_index:
                pg.draw.rect(surf, (0, 100, 0), option_rect)
            surf.blit(option, option_rect)

    def out(self):
        self._options.clear()
        self._in_shadow = True


running = True


def quit_game():
    global running
    running = False


def formation():
    window = Tk()
    window.title("formation")
    window.geometry("550x400")
    window.configure(bg='bisque2')
    window.resizable(False, False)

    text_var = []
    entries = []

    def get_mat():
        for i in range(rows):
            matrix.append([])
            for j in range(cols):
                matrix[i].append(text_var[i][j].get())
                if matrix[i][j] == '':
                    matrix[i][j] = "0"
        window.destroy()

        print(matrix)

    Label(window, text="Make a formation", font=('arial', 10, 'bold'),
          bg="bisque2").place(x=150, y=20)
    Label(window, text="◄⁞Θ⁞Θ⁞Θ⁞Θ⁞Ɒ - 1 ship", font=('arial', 10, 'bold'),
          bg="bisque2").place(x=370, y=150)
    Label(window, text="◄⁞Θ⁞Θ⁞Θ⁞Ɒ    - 2 ships", font=('arial', 10, 'bold'),
          bg="bisque2").place(x=370, y=200)
    Label(window, text="◄⁞Θ⁞Θ⁞Ɒ        - 3 ships", font=('arial', 10, 'bold'),
          bg="bisque2").place(x=370, y=250)
    Label(window, text="◄⁞Θ⁞Ɒ           - 4 ships", font=('arial', 10, 'bold'),
          bg="bisque2").place(x=370, y=300)

    x2 = 0
    y2 = 0
    rows, cols = (10, 10)
    for i in range(rows):

        text_var.append([])
        entries.append([])
        Label(window, text=i, font=('arial', 10, 'bold'), bg="bisque2").place(x=60 + i * 30 + 2, y=45)
        Label(window, text=i, font=('arial', 10, 'bold'), bg="bisque2").place(x=42, y=60 + i * 30 + 8)
        for j in range(cols):
            text_var[i].append(StringVar())
            entries[i].append(Entry(window, textvariable=text_var[i][j], width=3))
            entries[i][j].place(x=60 + x2, y=70 + y2)
            x2 += 30

        y2 += 30
        x2 = 0
    button = Button(window, text="Submit", bg='bisque3', width=15, command=get_mat)
    button.place(x=150, y=370)
    window.mainloop()


net1 = pg.image.load(r'net.png')
net2 = pg.image.load(r'net.png')
in_battle = False
alive = pg.image.load(r'alive.png')
dead = pg.image.load(r'dead.png')
miss = pg.image.load(r'miss.png')
"""win = pg.image.load(r'win.png')
lose = pg.image.load(r'lose.jpg')"""
to_render = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

i = 0


def draw_alive_ships():
    for i1 in range(10):
        for j1 in range(10):
            if matrix[i1][j1] == "1":
                net2.blit(alive, (j1 * 30, i1 * 30))
            elif matrix[i1][j1] == "3":
                net2.blit(dead, (j1 * 30, i1 * 30))
            elif matrix[i1][j1] == "2":
                net2.blit(miss, (j1 * 30, i1 * 30))
            pg.display.flip()


def draw_alive_ships2():
    for i1 in range(10):
        for j1 in range(10):
            if player.enemy_saved_matrix[i1][j1] == "1":
                net1.blit(alive, (i1 * 30, j1 * 30))
            elif player.enemy_saved_matrix[i1][j1] == "3":
                net1.blit(dead, (i1 * 30, j1 * 30))
            elif player.enemy_saved_matrix[i1][j1] == "2":
                net1.blit(miss, (i1 * 30, j1 * 30))
            pg.display.flip()

def battle():
    menu.out()
    playing = True



def draw_battle():
    if in_battle:
        screen.fill(BLACK)
        screen.blit(net2, (450, 100))
        screen.blit(net1, (50, 100))
        screen.blit(row_numbers, (50, 75))
        screen.blit(row_numbers, (450, 75))
        for i in range(9):
            col_numbers = COURIER.render(to_render[i], True, (180, 0, 0))
            screen.blit(col_numbers, (30, 105 + i * 30))
            col_numbers = COURIER.render(to_render[i], True, (180, 0, 0))
            screen.blit(col_numbers, (430, 105 + i * 30))
        col_numbers = COURIER.render("10", True, (180, 0, 0))
        screen.blit(col_numbers, (20, 375))
        col_numbers = COURIER.render("10", True, (180, 0, 0))
        screen.blit(col_numbers, (420, 375))
        draw_alive_ships()
        draw_alive_ships2()
    else:
        screen.fill(BLACK)
        menu.draw(screen, 100, 100, 75)


menu = Menu()
menu.append_option('Hello world!', lambda: print('Hello world!'))
menu.append_option('battle', battle)
menu.append_option('Your formation', formation)
menu.append_option('Quit', quit_game)


def shoot(x_sh, y_sh):
    if playing:
        global end_win
        print("_" * 10)
        draw_battle()
        pg.display.flip()
        message = ""
        try:
            message = messages.pop()#player.parse_server_message()
            print("something recived")
            print(message)
        except:
            print("Not your turn")
        if message == "hello":
            print(message)
        elif message == "your turn":
            print(message)
            x_sh = (x_sh - 50) // 30
            y_sh = (y_sh - 100) // 30
            if x_sh > 9:
                x_sh = 9
            if y_sh > 9:
                y_sh = 9
            # x = input("write raw: ")
            # y = input("write column: ")
            print(x_sh, y_sh)

            player.send_to_server(f"{y_sh} {x_sh}")
            draw_battle()
            pg.display.flip()
            data = ""
            try:
                data = messages.pop()#player.parse_server_message()
            except:
                print("something went wrong")
            print(data)

            x_sh = int(x_sh)
            if x_sh > 10:
                x_sh = 10
            y_sh = int(y_sh)
            if y_sh > 10:
                y_sh = 10

            if data == "killed":
                player.enemy_saved_matrix[x_sh][y_sh] = "3"
            else: #data == "hollow" and player.enemy_saved_matrix[x_sh][y_sh] != "3"
                player.enemy_saved_matrix[x_sh][y_sh] = "2"

            pprint.pprint(player.matrix)
            pprint.pprint(player.enemy_saved_matrix)
        elif message == "win":
            print("ggwp " + message)
            end_win = 1
        elif message == "lose":
            print("ggwp " + message)
            end_win = 2
        else:
            try:
                x_sh1, y_sh1 = message.split(" ")
                x_sh1 = int(x_sh1)
                if x_sh1 > 10:
                    x_sh1 = 10
                y_sh1 = int(y_sh1)
                if y_sh1 > 10:
                    y_sh1 = 10

                if player.matrix[x_sh1][y_sh1] == "1":
                    player.matrix[x_sh1][y_sh1] = "3"
                elif player.matrix[x_sh1][y_sh1] == "0":
                    player.matrix[x_sh1][y_sh1] = "2"
                draw_battle()
                pg.display.flip()
                pprint.pprint(player.matrix)
                pprint.pprint(player.enemy_saved_matrix)
                shoot(x_sh, y_sh)
            except:
                print("Not your turn")


end_win = 0

while running:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            quit_game()
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_w:
                menu.switch(-1)
            elif e.key == pg.K_s:
                menu.switch(1)
            elif e.key == pg.K_SPACE:
                if menu.selected() != 1:
                    menu.select()
                else:
                    in_battle = True
                    menu.select()
                    player = Player()
                    t1 = threading.Thread(target=thread_to_listen, args=(messages, player))
                    t1.start()
        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                x, y = e.pos
                shoot(x, y)
                print(e.pos)
    try:
        message = messages[0]
        x_sh1, y_sh1 = message.split(" ")
        x_sh1 = int(x_sh1)
        if x_sh1 > 10:
            x_sh1 = 10
        y_sh1 = int(y_sh1)
        if y_sh1 > 10:
            y_sh1 = 10

        if player.matrix[x_sh1][y_sh1] == "1":
            player.matrix[x_sh1][y_sh1] = "3"
        elif player.matrix[x_sh1][y_sh1] == "0":
            player.matrix[x_sh1][y_sh1] = "2"
        draw_battle()
        pg.display.flip()
    except:
        pass
    draw_battle()
    pg.display.flip()


