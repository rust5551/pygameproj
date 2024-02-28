import pygame
import ast
from itertools import groupby
import pygame_widgets
from pygame_widgets.button import Button


class ConnectFour():
    def __init__(self):
        pygame.init()
        self.size = self.width, self.height = 900, 700
        self.screen = pygame.display.set_mode(self.size)

        self.tx = False
        self.gamestarted = False
        self.gs = False
        self.running = True
        self.fps = 60
        self.radius = 40
        self.xval = 100
        self.yval = 100
        self.xshift = 50
        self.yshift = 0
        self.p1 = True
        self.movenum = 0
        self.win = False
        self.board = [[(0, 0, 0)] * 7 for _ in range(6)]
        self.circles = [[] for _ in range(6)]
        self.bgs = {7: (40, 40, 720, 620),
                    6: (40, 40, 620, 520),
                    5: (40, 40, 520, 420)}
        btnnames = ["Главное меню", "Загрузить", "Заново"]
        self.uifuncs = {0: self.mainmenu,
                        1: self.loadgame,
                        2: self.restart}
        
        self.my_image = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(self.my_image, (0, 0, 0, 200), self.my_image.get_rect())

        self.gameoverbtn = Button(self.my_image, 330, 275, 150, 75, text="Начать заново", onClick=self.restart)
        self.gameoverbtn.hide()

        self.fieldbuttons = []
        for i in range(3):
            btn = Button(self.screen, 120 * i + 270, 300, 100, 100, text=str(i), onClick=lambda x=i: self.selectfield(x))
            self.fieldbuttons.append(btn)
        
        self.uibuttons = []
        for i in range(3):
            btn = Button(self.screen, 770, 40 + 60 * i, 120, 50, text=btnnames[i], onClick=self.uifuncs[i])
            self.uibuttons.append(btn)
        for i in self.uibuttons:
            i.hide()

        for i in range(1, 7):
            for j in range(1, 8):
                self.circles[i - 1].append(pygame.draw.circle(self.screen, self.board[i - 1][j - 1], (j * self.xval + self.xshift - 50, i * self.yval + self.yshift), self.radius))

        self.clock = pygame.time.Clock()

        self.game()

    def game(self): # Главный цикл
        while self.running:
            pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.width, self.height))
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.gamestarted and self.gs:
                        clicked = []
                        pos = pygame.mouse.get_pos()
                        for line in self.circles:
                            for circ in line:
                                if circ.collidepoint(pos):
                                    clicked = circ
                        if clicked and not self.win and not self.check_full(self.board):
                            for line in self.circles:
                                if clicked in line:
                                    xc = line.index(clicked)
                                    yc = self.circles.index(line)
                                    break
                            self.p1 = self.move(self.p1, xc, yc)
                            self.gravitation(xc, yc)
                            self.winning()
                            self.drawboard()
                        elif self.check_full(self.board) and not self.win:
                            self.win = True
                            self.winstr = "НИЧЬЯ"
                    elif self.gamestarted and not self.gs:
                        self.gs = True
                if event.type == pygame.QUIT:
                    self.savegame()
                    self.running = False
            
            pygame_widgets.update(pygame.event.get())
            if self.gamestarted and not self.win:
                self.drawboard()
            elif self.win:
                self.drawboard()
                self.gameoverbtn.show()
                self.gameover()

            self.clock.tick(self.fps)
            
            pygame.display.flip()
            self.screen.fill((0, 0, 0))

        
    def start(self): # Начало игры  
        self.gamestarted = True
        for i in self.fieldbuttons:
            i.hide()
        for i in self.uibuttons:
            i.show()
    
    def mainmenu(self): # Главное меню
        self.gamestarted = False
        self.gs = False
        for i in self.fieldbuttons:
            i.show()
        for i in self.uibuttons:
            i.hide()

    def loadgame(self): # Загрузка игры по нажатию кнопки
        try:
            with open("save.txt", 'r') as sav:
                a = [i.strip() for i in sav.readlines()]
                self.fieldnum = int(a.pop(0))
                self.win = a.pop(0)
                b = [ast.literal_eval(i) for i in a]
                self.board = b
        except:
            pass

    def savegame(self): # Сохранение игры при выходе
        try:
            with open("save.txt", "a+", encoding="UTF-8") as sav:
                sav.truncate(0)
                sav.write(str(self.fieldnum) + '\n')
                if self.win:
                    sav.write(str(self.win) + '\n')
                else:
                    sav.write("" + '\n')
                for i in self.board:
                    sav.write(str(i) + '\n')
        except:
            pass

    def gameover(self): # Меню конца игры
        for i in self.uibuttons:
            i.hide()
        self.screen.blit(self.my_image, self.my_image.get_rect())
        self.gameoverbtn.show()
        font = pygame.font.SysFont(None, 65)
        text = font.render(self.winstr, True, (255, 255, 255))
        if not self.tx:
            self.my_image.blit(text, (200, 200))
            self.tx = True

    def selectfield(self, x): # Меню выбора поля
        match x:
            case 0:
                self.board = [[(0, 0, 0)] * 7 for _ in range(6)]
            case 1:
                self.board = [[(0, 0, 0)] * 6 for _ in range(5)]
            case 2:
                self.board = [[(0, 0, 0)] * 5 for _ in range(4)]
        self.fieldnum = x
        self.gamestarted = True
        for i in self.fieldbuttons:
            i.hide()
        for i in self.uibuttons:
            i.show()

    def restart(self): # Рестарт игры
        self.win = False
        self.gs = False
        self.tx = False
        self.my_image = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(self.my_image, (0, 0, 0, 200), self.my_image.get_rect())
        self.gameoverbtn = Button(self.my_image, 330, 275, 150, 75, text="Начать заново", onClick=self.restart)
        self.selectfield(self.fieldnum)
        self.gameoverbtn.hide()
        
    def drawboard(self): # Отрисовка доски
        pygame.draw.rect(self.screen, (120, 120, 120), self.bgs[len(self.board) + 1])
        for i in range(1, len(self.board) + 1):
            for j in range(1, len(self.board[i - 1]) + 1):
                pygame.draw.circle(self.screen, self.board[i - 1][j - 1], (j * self.xval + self.xshift - 50, i * self.yval + self.yshift), self.radius)
        
    def move(self, p1, xc, yc): # Ход
        if self.board[yc][xc] == (0, 0, 0) and p1:
            self.board[yc][xc] = (255, 0, 0)
            p1 = False
            self.movenum += 1
            return p1
        elif self.board[yc][xc] == (0, 0, 0) and not p1:
            self.board[yc][xc] = (254, 255, 0)
            p1 = True
            self.movenum += 1
            return p1
        return p1
        
    def gravitation(self, xc, yc): # Гравитация 
        if yc < len(self.board) - 1:
            for i in range(len(self.board) - 1 - yc):          
                if self.board[yc + 1][xc] == (0, 0, 0):
                    self.board[yc + 1][xc] = self.board[yc][xc]
                    self.board[yc][xc] = (0, 0, 0)
                yc += 1

    def winning(self):
        self.check_win(self.board) # Проверка по линиям
        self.check_win(self.transpose(self.board)) # Проверка по столбцам
        self.check_win(self.transpose(self.shift(self.board))) # Проверка по диагоналям
        self.check_win(self.transpose(self.shift(reversed(self.board)))) # Проверка по диагоналям

    def shift(self, board):
        return [self.padding(r) + row + self.padding(len(row) - r - 1) for r, row in enumerate(board)]
    
    def transpose(self, board):
        return [list(i) for i in zip(*board)]

    def padding(self, n):
        return [(0, 0, 0) for _ in range(n)]
            
    def check_win(self, board): # Проверка победы
        for i in range(len(board)):
            if self.win:
                break
            for _, j in groupby(board[i], lambda x: x[0]):
                elems = list(j)
                if len(elems) == 4 and elems[0] == (255, 0, 0):
                    self.winstr = "ПОБЕДА КРАСНЫХ"
                    self.win = True
                    break
                elif len(elems) == 4 and elems[0] == (254, 255, 0):
                    self.winstr = "ПОБЕДА ЖЁЛТЫХ"
                    self.win = True
                    break
        
    def check_full(self, board):
        for row in board:
            if (0, 0, 0) in row:
                return False
        return True


if __name__ == '__main__':
    a = ConnectFour()