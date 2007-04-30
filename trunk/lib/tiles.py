from pygext.gl.all import *
import pygame
from pygame.locals import *
import os
from euclid import *

TILE_SIZE = 32

def imgcolorkey(image, colorkey):
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
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
        return imgcolorkey(image, colorkey )

class Map:
    def __init__(self, mapname):
        spritesheet = SpriteSheet('blocks1.bmp')
        surf = spritesheet.imgat((444, 104, 32, 32),(0,0,0,255))
        surf2 = spritesheet.imgat((240, 2, 32, 32),(0,0,0,255))
        surf3 = spritesheet.imgat((172, 36, 32, 32),(0,0,0,255))
        surf4 = spritesheet.imgat((342, 36, 32, 32),(0,0,0,255))

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


class WfxMap:
    def __init__(self, mapname):
        self.spritesheet = SpriteSheet('tiles_0.png')
        surf_black = self.load_tile(4,1,(0,0,0,255) )
        surf_up_1 = self.load_tile(1,0,(0,0,0,255) )
        surf_up_2 = self.load_tile(2,0,(0,0,0,255) )
        surf_plain = self.load_tile(3,0,(0,0,0,255) )
        surf_down_2 = self.load_tile(1,1,(0,0,0,255) )
        surf_down_1 = self.load_tile(2,1,(0,0,0,255) )
        surf_semi_plain = self.load_tile(0,1,(0,0,0,255) )

        self.surf_color = {
            # key (color) : ( pygame surface, line coordinates )
            (0,0,0,255) : (None,None),
            (255,255,255,255) : (surf_plain, Line2(Point2(0,31),Point2(31,31))),
            (0,0,255,255) : (surf_up_1, Line2(Point2(0,0),Point2(31,15))),
            (0,0,128,255) : (surf_up_2, Line2(Point2(0,16),Point2(31,31))),
            (0,255,0,255) : (surf_down_2, Line2(Point2(0,31),Point2(31,16))),
            (0,128,0,255) : (surf_down_1, Line2(Point2(0,15),Point2(31,0))),
            }

        self.bg = {}
        img = load_image(mapname + '.bmp')
        self.w, self.h = img.get_width(),img.get_height()
        for j in range(0, self.h):
            # flip vertically
            fj = self.h - j - 1
            for i in range(0, self.w):
                cell = img.get_at((i, j))

                try:
                    surf,coord = self.surf_color[ cell ]
                    if surf:
                        self.bg[ (i,j) ] = (Entity(surf),coord)
                    else:
                        self.bg[ (i,j) ] = (None,None)
                except KeyError,e:
                    print cell
                    self.bg[ (i,j) ] = (None,None)


    def load_tile( self, x, y, color = None ):
        x = x * (  32 + 1) + 1
        y = y * (  32 + 1) + 1
        return self.spritesheet.imgat((x,y, 32, 32),color)
        
    def get_cell( self, x, y ):
        if x < 0 or x >= self.w:
            raise Exception("x out of bounds: %s" % x )
        if y < 0 or y >= self.h:
            raise Exception("y out of bounds: %s" % y )
        return self.bg[ (x,y) ][0]


    def get_h( self, real_x ):
        x = real_x / TILE_SIZE
        mod_x = real_x % TILE_SIZE
        for i in range( self.h ):
            surf,line= self.bg[ (x,i) ]
            if surf:
                m = float( (line.p2.y - line.p1.y) ) / float( (line.p2.x - line.p1.x) ) * mod_x + line.p1.y
                new_m = (TILE_SIZE-1) - m
                ret = (self.h-i) * TILE_SIZE - new_m
                return ret
        return 0
