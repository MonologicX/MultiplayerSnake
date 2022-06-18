from gameServer import *

class GameClient:
    def __init__(self, SERVER, PORT=31705):

        self.PORT = PORT
        self.SERVER = SERVER
        self.ADDRESS = (self.SERVER, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS)

        self.CLOCK = pygame.time.Clock()
        self.players = [self.rec(), self.rec()]

        self.main()

    def send(self, obj):
        self.client.send(pickle.dumps(obj))

    def rec(self):
        return pickle.loads(self.client.recv(10000))

    def draw(self):
        for player in self.players:
            player.draw()

    def main(self):

        gameOver = False
        while not gameOver:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.send(DISCONNECTOBJ())
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.players[0].move(move="RIGHT")
                    if event.key == pygame.K_LEFT:
                        self.players[0].move(move="LEFT")
                    if event.key == pygame.K_UP:
                        self.players[0].move(move="UP")
                    if event.key == pygame.K_DOWN:
                        self.players[0].move(move="DOWN")

            self.send(self.players[0])
            self.players[1] = self.rec()

            print("POS: ({0}, {1})".format(self.players[0].x, self.players[0].y))

            self.draw()
            self.CLOCK.tick(FPS)

c = GameClient("192.168.4.57")
