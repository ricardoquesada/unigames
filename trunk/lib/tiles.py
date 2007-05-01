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
    def __init__( self, *args, **kw ):
        
        self._setup_tiles = {}      # map of colors, and tile's configurations
        self._tile_cache = {}       # Entity(surfaces) and colors are cached here
        self._tiles = {}            # tiles and its coordinates

        # basic setup
        self.image_map = load_image( kw['map_name'] )
        self.spritesheet = SpriteSheet( kw['sprite_sheet'] )
        self.w, self.h = self.image_map.get_width(),self.image_map.get_height()


        self.init(args,kw)
        self.init_tiles()
        self.load_tiles()

    def init( self, args, kw ):
        # defined in subclasses
        pass
        
    def init_tiles(self):
        # defined in subclasses
        pass

    def load_tile_surface( self, x, y, color = None ):

        try:
            return self._tile_cache[(x,y)]
        except KeyError:
            x = x * ( TILE_SIZE + 1) + 1
            y = y * ( TILE_SIZE + 1) + 1
            surf = self.spritesheet.imgat((x,y, TILE_SIZE, TILE_SIZE),color)
            if surf:
                surf = Entity( surf )
            self._tile_cache[ (x,y) ] = surf
            return surf

    def load_tiles( self ):
        for j in range(0, self.h):
            for i in range(0, self.w):
                color = self.image_map.get_at((i, j))

                try:
                    cell = self._setup_tiles[ color ]
                    cell_surf = self.load_tile_surface( cell[0][0], cell[0][1], cell[1] )
                    self._tiles[ (i,j) ] = (cell_surf,cell)

                except KeyError,e:
                    print "Warning: Color [ %s ] has no associated surface" % str(color)
                    self._tiles[ (i,j) ] = (None,None)

    def get_h( self, real_x ):
        x = real_x / TILE_SIZE
        mod_x = real_x % TILE_SIZE
        for i in range( self.h ):
            surf,cell_conf= self._tiles[ (x,i) ]
            if surf:
                m = cell_conf[2][2] * mod_x + cell_conf[2][1]
                new_m = (TILE_SIZE-1) - m
                ret = (self.h-i) * TILE_SIZE - new_m
                return ret
        return 0

    def get_cell( self, x, y ):
        if x < 0 or x >= self.w:
            raise Exception("x out of bounds: %s" % x )
        if y < 0 or y >= self.h:
            raise Exception("y out of bounds: %s" % y )
        return self._tiles[ (x,y) ][0]


class DownHillMap(Map):
    def init( self, args, kw):
        pass

    def init_tiles( self):
        self._setup_tiles = {
            # (map_color) : ( (tile_x,tile_y), tile_alpha_color, (tile_origin_x, tile_origin_y, tile_slope)
#            (0,0,0,255) : ( (0,2), None, (0,31,0.0) ),              # blank tile

            (255,255,255,255) : ( (0,0), None, (0,31,0.0) ),        # line tile #1
            (255,255,192,255) : ( (1,0), None, (0,31,0.0) ),        # line tile #2
            (255,255,128,255) : ( (16,0), None, (0,31,0.0) ),       # line tile #2
            (255,255,64,255) : ( (17,0), None, (0,31,0.0) ),        # line tile #2

            (255,255,32,255) : ( (0,1), None, (0,31,0.0) ),        # dirt

            (255,0,255,255) : ( (2,0), None, (0,31,-0.5) ),        # slope -0.5 #1
            (255,32,255,255) : ( (3,0), None, (0,15,-0.5) ),        # slope -0.5 #2
            (255,64,255,255) : ( (4,1), None, (0,31,-1.0) ),        # slope -1 #2
        }
