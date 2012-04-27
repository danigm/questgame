#!/usr/bin/env python
import sys

import pygame
from pygame.locals import *

from utils import wrap_text, load_image
from questmap import Map
from mapobj import Tree, Guy


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.mode = "GAME"

        self.window = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Quest Game')
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.chat_surface = pygame.Surface((self.screen.get_width(), 50))
        self.chat_surface.fill(pygame.Color(255, 255, 255))
        self.chat_surface.set_alpha(130)
        self.text = ""
        self.font = pygame.font.SysFont("Sans", 16)

        self.map = Map(1, 1)
        self.map.load_from_image("maps/map1.png")

        self.guy1 = Guy("Character Boy.png", self.map, self.screen)
        self.guy1.set_pos(1, 1)
        self.guy1.set_pos(17, 0)
        self.map.scroll = [0, 14]

        tree1 = Tree(self.map)
        tree2 = Tree(self.map)
        tree3 = Tree(self.map)
        tree4 = Tree(self.map)
        tree2.set_pos(20, 0)
        tree1.set_pos(20, 1)
        tree3.set_pos(19, 2)
        tree4.set_pos(18, 3)

        self.events = {}

    def manage_game(self, event):
        if event.type == QUIT:
            sys.exit(0)
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit(0)
        elif event.type == KEYDOWN:
            self.events[event.key] = True
        elif event.type == KEYUP:
            if event.key == K_c:
                self.mode = "CHAT"
                self.text = ""
                pygame.key.set_repeat(300, 10)

            self.events[event.key] = False

    def manage_chat(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.mode = "GAME"
            pygame.key.set_repeat()
        if event.type == KEYDOWN and event.key == K_RETURN:
            self.guy1.set_text(self.text)
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

    def paint_chat(self):
        self.screen.blit(self.chat_surface, (0, self.screen.get_height() - self.chat_surface.get_height()))
        texts = wrap_text(self.font, self.text, self.screen.get_width() - 40)
        for i, t in enumerate(texts):
            font_surface = self.font.render(t, True, pygame.Color(0, 0, 0))
            self.screen.blit(font_surface, (20, (i * 20) + self.screen.get_height() - self.chat_surface.get_height()))

    def main(self):
        while True:
            self.clock.tick(60)
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

            # moving char
            self.guy1.update(self.events)

            # updating screen
            pygame.display.flip()


if __name__ == '__main__':
    game = Game()
    game.main()
