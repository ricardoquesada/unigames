from pygext.gl.all import *
import pygame
from pygame.locals import *
import os
from euclid import *
from pygame.color import Color

TW = 32
TH = 32
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
        
        self._tiles_config= {}      # map of colors, and tile's configurations

        # basic setup
        self._level = self.load_level( 'data/%s' % kw['map_name'] )
        self._tiles = self.load_tiles( 'data/%s' % kw['sprite_sheet'] )

        self.init(args,kw)
        self.init_tiles()

    def init( self, args, kw ):
        # defined in subclasses
        pass
        
    def init_tiles(self):
        # defined in subclasses
        pass

    # function "stealed" from: the old battleaxe 4
    def load_level(self, fname):
        img = pygame.image.load(fname)
        #return [[[img.get_at((x,y))[n] for x in xrange(0,img.get_width())] for y in xrange(0,img.get_height())] for n in xrange(0,4)]
        self.w,self.h = img.get_width(),img.get_height()
        l = [[[0 for x in xrange(0,self.w)] for y in xrange(0,self.h)] for n in xrange(0,3)]
        for y in xrange(0,self.h):
            for x in xrange(0,self.w):
                r,g,b,a = img.get_at((x,y))
                l[0][y][x] = r
                l[1][y][x] = g
                l[2][y][x] = b
        return l

    # function "stealed" from: the old battleaxe 4
    def load_tiles(self, fname):
        img = pygame.image.load(fname).convert_alpha()
        w,h = img.get_width()/TW,img.get_height()/TH
        return [ img.subsurface((n%w)*TW,(n/w)*TH,TW,TH) for n in xrange(0,w*h)]


    def get_tile_config( self, i ):
        try:
            return self._tiles_config[i]
        except KeyError:
            return None

    def get_tile( self, x, y ):
        c = self._level[0][y][x]
        if c == 0:
            return None

        return Entity( self._tiles[c] )

    def get_slope( self, x ):
        return 0.0

    def get_h( self, real_x, real_y ):
        return 0

    def get_h_and_slope( self, real_x ):
        return (0,0.0)


    def is_collision_right( self, x, y ):
        return False

    def is_collision_left( self, x,y ):
        return False
    
class DownHillMap(Map):
    def init( self, args, kw):
        pass

    def init_tiles( self):
        self._tiles_config= {

# transparent tile
0x00: [None,],

# floor
0x20: [None,]
        }

