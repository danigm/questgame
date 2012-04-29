'''
Utils functions for general purpose
'''

import os
import pygame
from pygame.locals import *


def wrap_text(font, text, max):
    texts = []
    words = text.split(" ")
    i = 0
    t = []
    while i < len(words):
        t.append(words[i])
        w, h = font.size(" ".join(t))
        if w >= max:
            texts.append(" ".join(t[0:-1]))
            t = [words[i]]
        i += 1

    texts.append(" ".join(t))
    return texts


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print "Cannot load image:", name
        raise SystemExit, message

    image = image.convert_alpha()
    #if colorkey is not None:
    #    if colorkey is -1:
    #        colorkey = image.get_at((0,0))
    #    image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def characters():
    names = [name for name in os.listdir('data') if name.startswith("Character")]
    return sorted(names)
