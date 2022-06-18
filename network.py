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

        print("[SERVER]: Starting Game")

    def handleClient(self, conn, addr, playerNum):

        if playerNum == 1:
            print("[SERVER]: PLAYER 1 CONNECTED")
            msgLen, msg = self.sendWithHeader(tupToStr(self.state[0]))
            conn.send(msgLen)
            conn.send(msg)
            msgLen, msg = self.sendWithHeader(tupToStr(self.state[1]))
            conn.send(msgLen)
            conn.send(msg)
        elif playerNum == 2:
            print("[SERVER]: PLAYER 2 CONNECTED")
            msgLen, msg = self.sendWithHeader(tupToStr(self.state[1]))
            conn.send(msgLen)
            conn.send(msg)
            msgLen, msg = self.sendWithHeader(tupToStr(self.state[0]))
            conn.send(msgLen)
            conn.send(msg)

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
                        msgLen, msg = self.sendWithHeader(tupToStr(self.state[1]))
                        conn.send(msgLen)
                        conn.send(msg)
                    elif playerNum == 2:
                        self.state[1] = strToTup(msg)
                        msgLen, msg = self.sendWithHeader(tupToStr(self.state[0]))
                        conn.send(msgLen)
                        conn.send(msg)

                print("[{0}]: {1}".format(addr, msg))

        conn.close()

    def sendWithHeader(self, message):

        msg = message.encode(self.FORMAT)

        msgLen = str(len(msg)).encode(self.FORMAT)
        msgLen += b'' * (self.HEADER - len(msgLen))

        return msgLen, msg

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

    def sendWithHeader(self, message):

        msg = message.encode(self.FORMAT)

        len = str(len(msg)).encode(self.FORMAT)
        len += b'' * (self.HEADER - len(len))

        self.client.send(len)
        self.client.send(msg)

    def recieve(self):

        msgLen = self.client.recv(self.HEADER).decode(self.FORMAT)

        if msgLen:

            msgLen = int(msgLen)

            msg = self.client.recv(msgLen).decode(self.FORMAT)

            print("MSG: {0}".format(msg))
            return msg
