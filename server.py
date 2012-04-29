import sys
import socket
import threading


class ClientControl(threading.Thread):

    def __init__(self, server, sock):
        self.server = server
        self.sock = sock
        threading.Thread.__init__(self)

    def run(self):

        while True:
            resp = self.sock.recv(1024)
            resp = resp.strip()
            print resp
            args = resp.split(" ")
            command = args[0]
            args = args[1:]

            if command == "EXIT":
                break

            self.server.send_all_minus(resp, self.sock)

        self.server.remove(self.sock)


class Server:
    def __init__(self, port=12345):
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.ss.bind(("", port))
            print "Server started at %s" % port
        except:
            print "ERROR biding port %s" % port
            sys.exit(1)

        self.ss.listen(10)
        self.sock = []
        self.addr = []

    def connect(self):
        while True:
            sock, addr = self.ss.accept()
            data = sock.recv(1024)
            data = data.strip()
            print "CONNECTED %s" % data
            self.sock.append(sock)
            self.addr.append(addr)

            ClientControl(self, sock).start()

    def close_all(self):
        for s in self.sock:
            s.send("EXIT \r\n")
            self.remove(s)
        self.sock = []
        self.addr = []

    def send_all_minus(self, str, sock):
        for s in self.sock:
            if s == sock:
                continue
            try:
                s.send(str + "\r\n")
            except:
                self.remove(sock)

    def send_to(self, str, sock):
        sock.send(str + "\r\n")

    def send_all(self, str):
        for s in self.sock:
            s.send(str + "\r\n")

    def remove(self, sock):
        sock.close()
        self.sock.remove(sock)


if __name__ == '__main__':
    ss = Server(12345)
    try:
        ss.connect()
    except KeyboardInterrupt:
        ss.close_all()
