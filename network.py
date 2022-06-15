import socket
import threading

def strToTup(str):
    str = str.split(',')
    return (int(str[0]), int(str[1]))

def tupToStr(tup):
    return "{0},{1}".format(tup[0], tup[1])

class Server:
    def __init__(self, PORT):

        self.PORT = PORT
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDRESS = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.HEADER = 64
        self.DISCONNECT_MSG = "!DISCONNECT"

        self.connections = threading.activeCount() - 1
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS)

        self.state = [(100, 100), (400, 400)]

        print("[SERVER]: START")
        self.start()

    def start(self):
        self.server.listen()

        print("[SERVER]: Listening on {0}".format(self.SERVER))

        while self.connections < 2:
            connection, address = self.server.accept()
            thread = threading.Thread(target=self.handleClient, args=(connection, address, self.connections + 1))
            thread.start()
            print("[SERVER]: {0} active connections.".format(threading.activeCount() - 1))
            self.connections = threading.activeCount() - 1

    def handleClient(self, conn, addr, playerNum):


        if playerNum == 1:
            conn.send(tupToStr(self.state[0]).encode(self.FORMAT))
            conn.send(tupToStr(self.state[1]).encode(self.FORMAT))
        elif playerNum == 2:
            conn.send(tupToStr(self.state[1]).encode(self.FORMAT))
            conn.send(tupToStr(self.state[0]).encode(self.FORMAT))

        print("[SERVER]: {0} connected".format(addr))

        connected = True
        while connected:

            msgLen = conn.recv(self.HEADER).decode(self.FORMAT)

            if msgLen:

                msgLen = int(msgLen)
                msg = conn.recv(msgLen).decode(self.FORMAT)

                if msg == self.DISCONNECT_MSG:
                    connected = False
                else:
                    if playerNum == 1:
                        self.state[0] = strToTup(msg)
                        conn.send(tupToStr(self.state[1]).encode(self.FORMAT))
                    elif playerNum == 2:
                        self.state[1] = strToTup(msg)
                        conn.send(tupToStr(self.state[0]).encode(self.FORMAT))

                print("[{0}]: {1}".format(addr, msg))

        conn.close()

class Client:
    def __init__(self, PORT, SERVER):

        self.HEADER = 64
        self.FORMAT = 'utf-8'
        self.PORT = PORT
        self.SERVER = SERVER
        self.ADDRESS = (self.SERVER, self.PORT)
        self.DISCONNECT_MSG = "!DISCONNECT"

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS)

    def send(self, message):

        msg = message.encode(self.FORMAT)

        len = str(len(msg)).encode(self.FORMAT)
        len += b'' * (self.HEADER - len(len))

        self.client.send(len)
        self.client.send(msg)
