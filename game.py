import pygame
import sys
import random
import math
from network import Server, Client, strToTup, tupToStr

WINWIDTH, WINHEIGHT = (1400, 1000)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARKRED = (139, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 139, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 139)

FPS = 20
BLOCKSIZE = 20

class Block:
    def __init__(self, WIN, x, y, border=True, color=BLACK, borderColor=WHITE):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        self.color = color
        self.border = border
        self.WIN = WIN

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

    def draw(self):

        pygame.draw.rect(self.WIN, self.color, self.rect)

        if self.border:
            pygame.draw.rect(self.WIN, self.borderColor, self.borderTop)
            pygame.draw.rect(self.WIN, self.borderColor, self.borderLeft)
            pygame.draw.rect(self.WIN, self.borderColor, self.borderRight)
            pygame.draw.rect(self.WIN, self.borderColor, self.borderBottom)

class Player:
    def __init__(self, startX, startY, WIN, color=BLUE, borderColor=DARKBLUE, startLen=3):
        self.WIN = WIN
        self.color = color
        self.borderColor = borderColor

        self.snake = [Block(self.WIN, startX, startY, color=self.color, borderColor=self.borderColor)]
        for i in range(startLen):
            self.snake.append(Block(self.WIN, self.snake[-1].x - BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        self.direction = "RIGHT"

        self.score = 0

    def move(self, move=None):

        if move == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
            self.snake[0].x -= BLOCKSIZE
        if move == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
            self.snake[0].x += BLOCKSIZE
        if move == "UP" and self.direction != "DOWN":
            self.direction = "UP"
            self.snake[0].y -= BLOCKSIZE
        if move == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"
            self.snake[0].y += BLOCKSIZE

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

    def draw(self):
        for part in self.snake:
            part.updateRect()
            part.draw()

    def addPiece(self):

        if self.direction == "RIGHT":
            self.snake.append(Block(self.WIN, self.snake[-1].x - BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        elif self.direction == "LEFT":
            self.snake.append(Block(self.WIN, self.snake[-1].x + BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        elif self.direction == "UP":
            self.snake.append(Block(self.WIN, self.snake[-1].x, self.snake[-1].y + BLOCKSIZE, color=self.color, borderColor=self.borderColor))
        elif self.direction == "DOWN":
            self.snake.append(Block(self.WIN, self.snake[-1].x, self.snake[-1].y - BLOCKSIZE, color=self.color, borderColor=self.borderColor))

class Food(Block):
    def __init__(self, WIN, color=GREEN, borderColor=DARKGREEN):
        super().__init__(WIN, random.randint(0, (WINWIDTH - BLOCKSIZE) / BLOCKSIZE) * BLOCKSIZE, random.randint(0, (WINHEIGHT - BLOCKSIZE) / BLOCKSIZE) * BLOCKSIZE, color=color, borderColor=borderColor)

    def checkForPlayerCollision(self, player):

        for part in player.snake:
            if part.rect.colliderect(self.rect):
                player.addPiece()
                return True

        return False

pygame.init()

WIN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
CLOCK = pygame.time.Clock()
c = Client(31705, "192.168.4.57")
startPos = strToTup(c.client.recv(2048).decode(c.FORMAT))
player = Player(startPos[0], startPos[1], WIN)
startPos2 = strToTup(c.client.recv(2048).decode(c.FORMAT))
player2 = Player(startPos2[0], startPos2[1], WIN)
players = [player, player2]
food = [Food(WIN), Food(WIN), Food(WIN), Food(WIN), Food(WIN), Food(WIN)]

def draw():
    WIN.fill(BLACK)
    for f in food:
        f.draw()
    for player in players:
        player.draw()

    pygame.display.update()
    CLOCK.tick(FPS)

gameOver = False
while not gameOver:

    move1 = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                move1 = "RIGHT"
            if event.key == pygame.K_LEFT:
                move1 = "LEFT"
            if event.key == pygame.K_UP:
                move1 = "UP"
            if event.key == pygame.K_DOWN:
                move1 = "DOWN"



    player.move(move=move1)
    for player in players:

        headRect = player.snake[0].rect
        for part in player.snake[2:]:
            if headRect.colliderect(part.rect):
                gameOver = True

        for p in players:
            if p != player:
                for part in p.snake:
                    if headRect.colliderect(part.rect):
                        gameOver = True

        for f in food:
            if f.checkForPlayerCollision(player):
                food.pop(food.index(f))
                food.append(Food(WIN))


    c.client.send(tupToStr((player.snake[0].x, player.snake[0].y)).encode(c.FORMAT))
    p2Pos = strToTup(c.client.recv(2048).decode(c.FORMAT))
    player2.snake[0].x = p2Pos[0]
    player2.snake[0].y = p2Pos[1]

    draw()

while gameOver:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
