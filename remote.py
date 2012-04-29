'''
Controls the game remotely for network gamming
'''

import socket
import threading
from mapobj import RemoteGuy


class RemoteGame:
    def __init__(self, game):
        self.game = game
        self.commands = {'MOVE': self.move,
                         'NEW': self.new_obj,
                         'DEL': self.del_obj,
                         'TALK': self.talk,
                         }
        self.running = True
        self.error = ""

        self.game.em.connect('game-event', self.threading_event)

        self.connect(game.server)

    def connect(self, server):
        host, port = server.split(':')
        port = int(port)
        self.socket = socket.socket()
        self.socket.settimeout(2)
        try:
            self.socket.connect((host, port))
            self.send("HELO %s" % self.game.player_name)
        except socket.error, msg:
            self.socket.close()
            self.error = 'socket ERROR'
            print "socket ERROR"
            return

        self.thread = threading.Thread(target=self.update)
        self.thread.start()

    def stop(self):
        self.send("EXIT")
        self.socket.close()
        self.running = False

    def update(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
            except Exception, e:
                continue
            data = data.strip()
            try:
                args = data.split(' ')
                command = args[0]
                args = args[1:]

                if command == "EXIT":
                    self.socket.close()
                    break

                self.commands[command](*args)
            except Exception, e:
                self.send("COMMAND ERROR: %s" % e)

    def send(self, data):
        ENDL = '\r\n'
        return self.socket.send(data + ENDL)

    def move(self, klass, objname, x, y):
        x = int(x)
        y = int(y)
        o = self.game.map.get_obj(objname)

        if not o:
            self.new_obj(klass, objname, x, y)
        else:
            o.set_pos(x, y)

    def new_obj(self, klass, name, x, y):
        x = int(x)
        y = int(y)
        klass = int(klass)
        o = RemoteGuy(klass, self.game)
        o.name = name
        o.set_pos(x, y)

    def del_obj(self, name):
        self.game.map.rm_obj(name)

    def talk(self, name, *args):
        text = ' '.join(args)
        text = text.decode('utf-8')
        o = self.game.map.get_obj(name)
        if o:
            o.set_text(text)

    def not_implemented(self, *args):
        self.send("NOT IMPLEMENTED")

    def game_event(self, data):
        if not self.error:
            self.send(data)

    def threading_event(self, data):
        t = threading.Thread(target=self.game_event, args=(data,))
        t.start()
