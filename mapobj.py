'''
Generic map object to inheritance
'''

import pygame
from pygame.locals import *

from utils import wrap_text, load_image, characters
from movements import *


class MapObj(pygame.sprite.Sprite):
    def __init__(self, image, game, *args, **kwargs):
        super(MapObj, self).__init__(*args, **kwargs)
        self.image, self.rect = load_image(image)
        self.text_img, _ = load_image("text.png")
        self.rect.x = 0
        self.rect.y = -40

        self.game = game
        self.map = self.game.map
        self.map.add(self)
        self.name = "obj-%d" % len(self.map.objects)
        self.text = ""
        self.text_counter = 0
        self.text_flipped = False

        self.font = pygame.font.SysFont("Sans", 16)

    def screen_pos(self):
        x = self.rect.x // 100
        y = (self.rect.y + 40) // 80
        return x, y

    def map_pos(self):
        si, sj = self.map.scroll
        x = self.rect.x // 100
        y = (self.rect.y + 40) // 80
        return x - sj, y - si

    def set_pos(self, x, y):
        self.rect.x = x * 100
        self.rect.y = (y * 80) - 40

    def draw(self, screen):
        si, sj = self.map.scroll
        y = self.rect.y - si * 80
        x = self.rect.x - sj * 100
        screen.blit(self.image, (x, y))

    def draw_text(self, screen):
        if self.get_text():
            si, sj = self.map.scroll
            y = self.rect.y - si * 80
            x = self.rect.x - sj * 100

            sx, sy = self.map_pos()
            if sy > 1:
                y = y - 80
                if self.text_flipped:
                    c = self.text_counter
                    self.set_text(self.text)
                    self.text_counter = c
            else:
                y = y + 120

                if not self.text_flipped:
                    c = self.text_counter
                    self.set_text(self.text)
                    self.text_counter = c

            screen.blit(self.text_surface, (x, y))

    def set_text(self, text):
        self.text_flipped = False
        self.text_surface = self.text_img.copy()
        sx, sy = self.map_pos()
        margin = 20
        if sy <= 1:
            margin = 30
            self.text_surface = pygame.transform.flip(self.text_surface, False, True)
            self.text_flipped = True

        self.text = text
        size = self.font.size(self.text)
        max_width = self.text_surface.get_width() - 40;
        if size[0] > max_width:
            texts = wrap_text(self.font, self.text, max_width)
        else:
            texts = [self.text]

        for i, t in enumerate(texts):
            font_surface = self.font.render(t, True, pygame.Color(0, 0, 0))
            self.text_surface.blit(font_surface, (20, (i + 1) * margin))

        self.text_counter = 100 + len(text) * 3

    def get_text(self):
        if self.text_counter:
            self.text_counter -= 1
        return self.text if self.text_counter else ""

    def collision(self, obj):
        return True

    def move_to(self, x, y):
        r = self.rect.copy()

        sx, sy = self.screen_pos()
        self.set_pos(sx + x, sy + y)

        if not self.map.can_move(self):
            self.rect = r

    def update(self, events):
        pass


class Tree(MapObj):
    def __init__(self, game):
        super(Tree, self).__init__("Tree Short.png", game)

    def collision(self, obj):
        self.set_text("Soy el arbol %s" % self.name)
        return False


class Guy(MapObj):
    def __init__(self, image, game, *args, **kwargs):
        super(Guy, self).__init__(image, game, *args, **kwargs)

        self.steps = 1
        self.maxsteps = 6
        self.reset = True
        self.screen = self.game.screen
        self.name = "Player"

    def move(self, events):
        r = self.rect.copy()
        x, y = self.screen_pos()
        si, sj = self.map.scroll

        if events.get(K_DOWN, False):
            self.set_pos(x, y + 1)
            if (self.rect.y + 160) - 80 * si >= self.screen.get_height():
                self.map.scroll = [si + 1, sj]

            self.game.em.signal('game-event', 'MOVE %s %s %s' % (self.name, 0, 1))
        elif events.get(K_UP, False):
            self.set_pos(x, y - 1)
            if (self.rect.y) - 80 * si < 0:
                self.map.scroll = [si - 1, sj]

            self.game.em.signal('game-event', 'MOVE %s %s %s' % (self.name, 0, -1))
        elif events.get(K_LEFT, False):
            self.set_pos(x - 1, y)
            if (self.rect.x) - 100 * sj < 0:
                self.map.scroll = [si, sj - 1]

            self.game.em.signal('game-event', 'MOVE %s %s %s' % (self.name, -1, 0))
        elif events.get(K_RIGHT, False):
            self.set_pos(x + 1, y)
            if (self.rect.x + 200) - 100 * sj >= self.screen.get_width():
                self.map.scroll = [si, sj + 1]

            self.game.em.signal('game-event', 'MOVE %s %s %s' % (self.name, 1, 0))
        else:
            self.reset = True

        if not self.map.can_move(self):
            self.rect = r

        if self.map.scroll[0] < 0:
            self.map.scroll[0] = 0
        if self.map.scroll[1] < 0:
            self.map.scroll[1] = 0

    def update(self, events):
        if self.reset:
            self.reset = False
            self.move(events)
            return

        elif self.steps % self.maxsteps:
            self.steps = self.steps + 1
            return
        else:
            self.steps = 1

        self.move(events)


class RemoteGuy(Guy):
    imgs = characters()
    def __init__(self, game, *args, **kwargs):
        image = self.imgs[kwargs.pop('idx', 0)]
        super(RemoteGuy, self).__init__(image, game, *args, **kwargs)
        self.maxsteps = 20
        self.movement = 'no'
        self.movements = {'no': no_movement,
                          'random': random_movement,
                          'horitonal': linear(1),
                          'vertical': linear(2),
                          'circular': circular(3)
                         }

    def move(self, events):
        self.movements[self.movement](self)

    def collision(self, obj):
        self.set_text("Hola, me llamo %s" % self.name)
        return False
