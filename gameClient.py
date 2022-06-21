from gameServer import *

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
