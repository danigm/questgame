#!/usr/bin/env python
import sys
import os

import pygame
from pygame.locals import *


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print "Cannot load image:", name
        raise SystemExit, message
    #image = image.convert()
    #if colorkey is not None:
    #    if colorkey is -1:
    #        colorkey = image.get_at((0,0))
    #    image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bricks = [[1] * width for i in range(height)]
        self.images = [0]
        self.objects = []
        self.scroll = [0, 0]

        self.block_names = [
            'Water Block.png',
            'Wall Block Tall.png',
            'Stone Block Tall.png',
            'Brown Block.png',
            'Dirt Block.png',
            'Grass Block.png',
            'Plain Block.png',
            'Stone Block.png',
            'Wall Block.png',
            'Wood Block.png',
        ]

        self.block_limit = 3

        for i in self.block_names:
            im, self.rect = load_image(i)
            self.images.append(im)

    def add(self, obj):
        self.objects.append(obj)

    def load_from_image(self, image):
        img, rect = load_image(image)
        self.width = rect.width
        self.height = rect.height - 1
        self.bricks = [[0] * self.width for i in range(self.height)]
        # first line color mapping
        mapping = {}
        for j in range(rect.width):
            color = img.get_at((j, 0))
            if color.a == 0:
                break

            mapping[(color.r, color.g, color.b, color.a)] = j + 1

        for i in range(1, rect.height):
            for j in range(rect.width):
                color = img.get_at((j, i))
                self.bricks[i - 1][j] = mapping.get((color.r, color.g, color.b, color.a), 0)

    def get_brick(self, i, j):
        si, sj = self.scroll
        i = i + si
        j = j + sj
        if i >= self.height or j >= self.width:
            return 0
        return self.bricks[i][j]

    def draw(self, screen):
        w, h = screen.get_size()
        for i in range((h // 80) + 1):
            for j in range((w // 100) + 1):
                self.rect.x = 100 * j
                self.rect.y = 80 * i
                idx = self.get_brick(i, j)
                if idx:
                    screen.blit(self.images[idx], (self.rect.x, self.rect.y))

            for o in self.objects:
                x, y = o.map_pos()
                if y == i:
                    o.draw(screen)

    def can_move(self, pos):
        x, y = pos
        if y >= len(self.bricks) or x >= len(self.bricks[0]) or x < 0 or y < 0:
            return False

        if self.bricks[y][x] > 3:
            return True
        else:
            return False


class MapObj(pygame.sprite.Sprite):
    def __init__(self, image, m, *args, **kwargs):
        super(MapObj, self).__init__(*args, **kwargs)
        self.image, self.rect = load_image(image)
        self.rect.x = 0
        self.rect.y = -40

        self.map = m
        self.map.add(self)

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


class Guy(MapObj):
    def __init__(self, image, m, *args, **kwargs):
        super(Guy, self).__init__(image, m, *args, **kwargs)

        self.steps = 1
        self.maxsteps = 10
        self.reset = True

    def move(self, events):
        r = self.rect.copy()
        x, y = self.screen_pos()
        si, sj = self.map.scroll

        if events.get(K_DOWN, False):
            self.set_pos(x, y + 1)
            if (self.rect.y + 160) - 80 * si >= self.screen.get_height():
                self.map.scroll = [si + 1, sj]
        elif events.get(K_UP, False):
            self.set_pos(x, y - 1)
            if (self.rect.y) - 80 * si < 0:
                self.map.scroll = [si - 1, sj]
        elif events.get(K_LEFT, False):
            self.set_pos(x - 1, y)
            if (self.rect.x) - 100 * sj < 0:
                self.map.scroll = [si, sj - 1]
        elif events.get(K_RIGHT, False):
            self.set_pos(x + 1, y)
            if (self.rect.x + 200) - 100 * sj >= self.screen.get_width():
                self.map.scroll = [si, sj + 1]
        else:
            self.reset = True

        if not self.map.can_move(self.screen_pos()):
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


def main():
    pygame.init()
    window = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Quest Game')
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    m = Map(4, 3)
    m.load_from_image("maps/map1.png")
    #for i in range(4):
    #    for j in range(3):
    #        m.bricks[j][i] = 1

    #m.bricks[0][0] = 3
    #m.bricks[0][1] = 3
    #m.bricks[0][2] = 3
    #m.bricks[1][1] = 4
    #m.bricks[1][0] = 4
    #m.bricks[1][2] = 3
    #m.bricks[2][2] = 3
    #m.bricks[2][3] = 3
    im, rect = load_image("Brown Block.png")
    guy1 = Guy("Character Boy.png", m)
    guy1.screen = screen
    guy1.set_pos(1, 1)
    #tree1 = MapObj("Tree Tall.png", m)
    #tree2 = MapObj("Tree Short.png", m)
    #tree1.set_pos(1, 1)
    #tree2.set_pos(1, 2)

    events = {}

    while True:
        clock.tick(60)
        screen.fill(pygame.Color(0, 0, 0, 1))

        # drawing
        rect.x = 0
        rect.y = 0

        m.draw(screen)

        # managing events
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                events[event.key] = True
            elif event.type == KEYUP:
                events[event.key] = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)
            else:
                pass
                #print event

        # moving char
        guy1.update(events)

        # updating screen
        pygame.display.flip()


if __name__ == '__main__':
    main()
