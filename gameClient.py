import pygame
import random
import pickle
import socket
import threading
import sys

WINWIDTH, WINHEIGHT = (900, 1000)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARKRED = (139, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 139, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 139)

BLOCKSIZE = 20

FPS = 20

class Block:
    def __init__(self, x, y, border=True, color=BLACK, borderColor=WHITE):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        self.color = color
        self.border = border

        if self.border:
            self.borderColor = borderColor
            self.borderTop = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE / 10)
            self.borderLeft = pygame.Rect(self.x, self.y, BLOCKSIZE / 10, BLOCKSIZE)
            self.borderBottom = pygame.Rect(self.x, self.y + (BLOCKSIZE - BLOCKSIZE / 10), BLOCKSIZE, BLOCKSIZE / 10)
            self.borderRight = pygame.Rect(self.x + (BLOCKSIZE - BLOCKSIZE / 10), self.y, BLOCKSIZE / 10, BLOCKSIZE)

    def updateRect(self):
        self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        if self.border:
            self.borderTop = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE / 10)
            self.borderLeft = pygame.Rect(self.x, self.y, BLOCKSIZE / 10, BLOCKSIZE)
            self.borderBottom = pygame.Rect(self.x, self.y + (BLOCKSIZE - BLOCKSIZE / 10), BLOCKSIZE, BLOCKSIZE / 10)
            self.borderRight = pygame.Rect(self.x + (BLOCKSIZE - BLOCKSIZE / 10), self.y, BLOCKSIZE / 10, BLOCKSIZE)

    def draw(self, WIN):

        pygame.draw.rect(WIN, self.color, self.rect)

        if self.border:
            pygame.draw.rect(WIN, self.borderColor, self.borderTop)
            pygame.draw.rect(WIN, self.borderColor, self.borderLeft)
            pygame.draw.rect(WIN, self.borderColor, self.borderRight)
            pygame.draw.rect(WIN, self.borderColor, self.borderBottom)

class Player:
    def __init__(self, startX, startY, color=BLUE, borderColor=DARKBLUE, startLen=3):
        self.color = color
        self.borderColor = borderColor

        self.snake = [Block(startX, startY, color=self.color, borderColor=self.borderColor)]
        for i in range(startLen):
            self.snake.append(Block(self.snake[-1].x - BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        self.direction = "RIGHT"

        self.food = []

    def move(self, move=None):

        if move == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
            self.snake[0].x -= BLOCKSIZE
        elif move == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
            self.snake[0].x += BLOCKSIZE
        elif move == "UP" and self.direction != "DOWN":
            self.direction = "UP"
            self.snake[0].y -= BLOCKSIZE
        elif move == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"
            self.snake[0].y += BLOCKSIZE
        else:
            move == None

        if move == None:
            if self.direction == "RIGHT":
                self.snake[0].x += BLOCKSIZE
            elif self.direction == "LEFT":
                self.snake[0].x -= BLOCKSIZE
            elif self.direction == "UP":
                self.snake[0].y -= BLOCKSIZE
            elif self.direction == "DOWN":
                self.snake[0].y += BLOCKSIZE

        if self.snake[0].x >= WINWIDTH:
            self.snake[0].x = 0
        if self.snake[0].x < 0:
            self.snake[0].x = WINWIDTH - BLOCKSIZE
        if self.snake[0].y >= WINHEIGHT:
            self.snake[0].y = 0
        if self.snake[0].y < 0:
            self.snake[0].y = WINHEIGHT - BLOCKSIZE

        for part in self.snake[::-1]:
            if self.snake.index(part) != 0:
                part.x = self.snake[self.snake.index(part) - 1].x
                part.y = self.snake[self.snake.index(part) - 1].y

    def draw(self, WIN):
        for part in self.snake:
            part.updateRect()
            part.draw(WIN)

    def addPiece(self):

        if self.direction == "RIGHT":
            self.snake.append(Block(self.snake[-1].x - BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        elif self.direction == "LEFT":
            self.snake.append(Block(self.snake[-1].x + BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        elif self.direction == "UP":
            self.snake.append(Block(self.snake[-1].x, self.snake[-1].y + BLOCKSIZE, color=self.color, borderColor=self.borderColor))
        elif self.direction == "DOWN":
            self.snake.append(Block(self.snake[-1].x, self.snake[-1].y - BLOCKSIZE, color=self.color, borderColor=self.borderColor))

class Food(Block):
    def __init__(self, color=GREEN, borderColor=DARKGREEN):
        super().__init__(random.randint(0, (WINWIDTH - BLOCKSIZE) / BLOCKSIZE) * BLOCKSIZE, random.randint(0, (WINHEIGHT - BLOCKSIZE) / BLOCKSIZE) * BLOCKSIZE, color=color, borderColor=borderColor)

class DISCONNECTOBJ:
    def __init__(self):
        pass


pygame.init()
WIN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

class GameClient:
    def __init__(self, SERVERIP="192.168.4.57", PORT=31705):

        self.PORT = PORT
        self.SERVER = SERVERIP
        self.ADDRESS = (self.SERVER, self.PORT)

        self.CLOCK = pygame.time.Clock()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS)

        self.players = [self.rec(), self.rec()]
        self.food = self.rec()

        self.main()

    def send(self, obj):
        self.client.send(pickle.dumps(obj))

    def rec(self):
        return pickle.loads(self.client.recv(20000))

    def draw(self):

        WIN.fill(BLACK)

        for player in self.players:
            player.draw(WIN)

        for food in self.food:
            food.draw(WIN)

        pygame.display.update()

    def main(self):

        gameOver = False
        while not gameOver:

            move = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.send(DISCONNECTOBJ())
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        move = "RIGHT"
                    if event.key == pygame.K_LEFT:
                        move = "LEFT"
                    if event.key == pygame.K_UP:
                        move = "UP"
                    if event.key == pygame.K_DOWN:
                        move = "DOWN"


            self.players[0].move(move=move)

            for food in self.food:
                if self.players[0].snake[0].rect.colliderect(food.rect):
                    self.players[0].addPiece()
                    self.food[self.food.index(food)] = Food()
                    self.send(self.food)


            self.send(self.players[0])
            self.players[1] = self.rec()
            self.food = self.rec()
            #print("POS: ({0}, {1})".format(self.players[0].snake[0].x, self.players[0].snake[0].y))

            self.draw()
            self.CLOCK.tick(FPS)

c = GameClient()
