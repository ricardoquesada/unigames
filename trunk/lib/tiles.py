from pygext.gl.all import *
import pygame
from pygame.locals import *
import os
from euclid import *
from pygame.color import Color

TW = 32     # TILE WIDTH SIZE
TH = 32     # TILE HEIGHT SIZE
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
        self.w = img.get_width()
        self.h = img.get_height()

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


    def get_tile_type( self, x, y ):
        c = self._level[0][y][x]
        return c

    def get_tile_config( self, x, y):
        c = self._level[0][y][x]
        try:
            c = self._tiles_config[c]
            return c
        except KeyError:
            return None

    def get_tile( self, x, y ):
        c = self._level[0][y][x]
        if c == 0:
            return None
        return Entity( self._tiles[c] )

    def get_slope( self, real_x ):
        # retutn the height for x, and the slope
        x = real_x / TW 
        mod_x = real_x % TW
        for i in xrange( self.h ):
            c = self.get_tile_config( x, i)
            if c:
                return c[2]
        return (0.0)


    def get_h_and_slope( self, real_x, real_y ):
        # retutn the height for x, and the slope
        x = real_x / TW 
        y = int(real_y / TH)
        mod_x = real_x % TW
        for i in xrange( y, self.h ):
            c = self.get_tile_config( x, i)
            if c:
                m = c[2] * mod_x + c[1]
                ret = i * TH - m
                return (ret, c[2] )
        return (self.h * TH,0.0)


    def is_collision_right( self, x, y ):
        if x % TW <  TW / 2:
            return False
        limit_x = (x / TW) * TW
        h1,s = self.get_h_and_slope( limit_x + TW - 1, y)
        h2,s = self.get_h_and_slope( limit_x + TW, y )

        if y < h2:
            return False
        if h1 - h2 > 5:
            return True
        return False

    def is_collision_left( self, x, y ):
        if x % TW >  TW / 2:
            return False
        limit_x = (x / TW ) * TW
        h1,s = self.get_h_and_slope( limit_x, y )
        h2,s = self.get_h_and_slope( limit_x - 1, y )

        if y < h2:
            return False
        if h1 - h2 > 5:
            return True
        return False
    
class DownHillMap(Map):
    def init( self, args, kw):
        pass

    def init_tiles( self):
        self._tiles_config= {

#key: tile id, value: (x,y,slope)

# transparent tile
#0x00: (0,31,0.0),

# floor
0x20: (0,31,0.0),
0x21: (0,31,0.0),
0x25: (0,31,0.0),
0x26: (0,31,0.0),

# slopes down
0x01: (0,10,-0.3),
0x02: (0,31,-1.0),
0x04: (0,31,-1.0),
0x10: (0,31,-1),
0x31: (0,31,-1.0), #dino
0x42: (0,31,-1.0), #dino
0x53: (0,31,-1.0), #dino

# down and up
0x07: (0,31,-0.48),
0x12: (0,31,-0.48),
0x13: (0,17,-0.161),
0x14: (0,12, 0.161),
0x15: (0,16, 0.48),
0x17: (0,16,0.48),


# slopes up
0x06: (0,0,1.0),
0x16: (0,0,0.6),
0x46: (0,0,1),

# dirt
0x30: (0,31,0.0),
0x40: (0,31,0.0), #dino
0x41: (0,31,0.0), #dino
0x50: (0,31,0.0), #dino
0x51: (0,31,0.0), #dino
0x52: (0,31,0.0), #dino
0x60: (0,31,0.0), #dino
0x61: (0,31,0.0), #dino
0x62: (0,31,0.0), #dino

}

