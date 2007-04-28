from pygext.gl.all import *
import pygame
from pygame.locals import *
import os

TILE_SIZE = 32

def imgcolorkey(image, colorkey):
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
            print colorkey
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_image(filename, colorkey = None):
    filename = os.path.join('data', filename)
    image = pygame.image.load(filename).convert()
    return imgcolorkey(image, colorkey)

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = load_image(filename)

    def imgat(self, rect, colorkey = None):
        rect = Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        return imgcolorkey(image, (0,0,0,255) )

class Map:
    def __init__(self, mapname):
        spritesheet = SpriteSheet('blocks1.bmp')
        surf = spritesheet.imgat((444, 104, 32, 32))
        surf2 = spritesheet.imgat((240, 2, 32, 32))
        surf3 = spritesheet.imgat((172, 36, 32, 32))
        surf4 = spritesheet.imgat((342, 36, 32, 32))

        self.bg = {}
        img = load_image(mapname + '.bmp')
        self.w, self.h = img.get_width(),img.get_height()
        for j in range(0, self.h):
            # flip vertically
            fj = self.h - j - 1
            for i in range(0, self.w):
                cell = img.get_at((i, j))
                if cell == (0,0,0,255):
                    self.bg[ (i,j) ] =  Entity(surf)
                elif cell == (255,0,0,255):
                    self.bg[ (i,j) ] =  Entity(surf2)
                elif cell == (168,168,168,255):
                    self.bg[ (i,j) ] =  Entity(surf3)
                elif cell == (0,255,0,255):
                    self.bg[ (i,j) ] = Entity(surf4)
                else:
#                    print cell
                    self.bg[ (i,j) ] = None

    def get_cell( self, x, y ):
        if x < 0 or x >= self.w:
            raise Exception("x out of bounds: %s" % x )
        if y < 0 or y >= self.h:
            raise Exception("y out of bounds: %s" % y )
        return self.bg[ (x,y) ]


    def get_h( self, x ):
        x /= TILE_SIZE
        for i in range( self.h ):
            if self.bg[ (x,i) ]:
                return (self.h-i) * TILE_SIZE
        return 0
