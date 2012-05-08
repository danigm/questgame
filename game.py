#!/usr/bin/env python
import sys

import pygame
from pygame.locals import *

from utils import wrap_text, load_image, load_config
from questmap import Map
from mapobj import Tree, Guy, RemoteGuy
from remote import RemoteGame

from events import EventManager, Event

CONFIG_FILE = "config.yml"


class Game:
    def __init__(self, server='', player='p1', idx=0):
        pygame.init()
        pygame.font.init()

        self.em = EventManager()
        self.em.add_event(Event("game-event"))

        self.config = load_config(CONFIG_FILE)
        self.menu_options = self.config['MENU']

        self.idx = idx
        self.mode = "GAME"
        self.server = server
        self.player_name = player

        self.remote_game = None
        if self.server:
            self.remote_game = RemoteGame(self)

        self.window = pygame.display.set_mode((self.config['SCREENHEIGHT'], self.config['SCREENWIDTH']))
        pygame.display.set_caption(self.config['TITLE'])
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.chat_surface = pygame.Surface((self.screen.get_width(), 50))
        self.chat_surface.fill(pygame.Color(255, 255, 255))
        self.chat_surface.set_alpha(130)
        self.menu_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height() // 2))
        self.menu_surface.fill(pygame.Color(255, 255, 255))
        self.menu_surface.set_alpha(130)
        self.text = ""
        self.font = pygame.font.SysFont("Sans", 16)

        self.map = Map(1, 1)
        self.map.load_from_image(self.config['MAP'])
        self.map.scroll = [0, 14]

        self.guy1 = Guy(self.idx, self)
        self.guy1.set_name(self.player_name)
        self.guy1.set_pos(17, 0)

        self.guy2 = RemoteGuy(1, self)
        self.guy2.set_name("Cat girl")
        self.guy2.movement = "circular"
        self.guy2.set_pos(15, 0)

        tree1 = Tree(self, 0)
        tree2 = Tree(self, 1)
        tree3 = Tree(self, 1)
        tree4 = Tree(self, 2)
        tree2.set_pos(20, 0)
        tree1.set_pos(20, 1)
        tree3.set_pos(19, 2)
        tree4.set_pos(18, 3)

        self.events = {}

    def manage_game(self, event):
        if event.type == QUIT:
            self.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            self.exit()
        elif event.type == KEYDOWN:
            self.events[event.key] = True
        elif event.type == KEYUP:
            if event.key == K_c:
                self.mode = "CHAT"
                self.text = ""
                pygame.key.set_repeat(300, 10)
            if event.key == K_m:
                self.mode = "MENU"

            self.events[event.key] = False

    def manage_chat(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.mode = "GAME"
            pygame.key.set_repeat()
        if event.type == KEYDOWN and event.key == K_RETURN:
            self.guy1.set_text(self.text)
            self.em.signal('game-event', 'TALK %s %s' % (self.player_name, self.text))
            self.mode = "GAME"
            pygame.key.set_repeat()
        if event.type == KEYDOWN:
            t = event.unicode
            if event.key == K_BACKSPACE:
                self.text = self.text[0:-1]
                t = ''
            elif event.key == K_TAB:
                t = "  "

            if len(self.text) < 141:
                self.text += t

    def manage_menu(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.mode = "GAME"
        for option in self.menu_options:
            #print option
            pass

    def paint_chat(self):
        self.screen.blit(self.chat_surface, (0, self.screen.get_height() - self.chat_surface.get_height()))
        texts = wrap_text(self.font, self.text, self.screen.get_width() - 40)
        for i, t in enumerate(texts):
            font_surface = self.font.render(t, True, pygame.Color(0, 0, 0))
            self.screen.blit(font_surface, (20, (i * 20) + self.screen.get_height() - self.chat_surface.get_height()))

    def main(self):
        while True:
            #print self.clock.get_fps()
            self.clock.tick(self.config['FPS'])
            self.screen.fill(pygame.Color(0, 0, 0, 1))

            self.map.draw(self.screen)

            if self.mode == "CHAT":
                self.paint_chat()

            # managing events
            for event in pygame.event.get():
                if self.mode == "GAME":
                    self.manage_game(event)
                if self.mode == "CHAT":
                    self.manage_chat(event)
                if self.mode == "MENU":
                    self.manage_menu(event)

            self.map.update(self.events)

            # updating screen
            pygame.display.flip()

    def exit(self):
        if self.remote_game:
            self.remote_game.stop()
        sys.exit(0)


if __name__ == '__main__':
    import getopt

    server = ''
    name = 'p1'
    idx = 0
    optlist, args = getopt.getopt(sys.argv[1:], 's:n:p:')
    for opt, arg in optlist:
        if opt == '-s':
            server = arg
        elif opt == '-n':
            name = arg
        elif opt == '-p':
            idx = int(arg)

    game = Game(server=server, player=name, idx=idx)
    try:
        game.main()
    except KeyboardInterrupt:
        game.exit()
