from pygext.gl.all import *
import os,pygame
from pygame.locals import *

TILE_SIZE = 32
TILES_X = 22
TILES_Y = 22

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
        return imgcolorkey(image, colorkey)

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
                    self.bg[ (i,j) ] = Entity(surf)
                elif cell == (255,0,0,255):
                    self.bg[ (i,j) ] = Entity(surf2)
                elif cell == (168,168,168,255):
                    self.bg[ (i,j) ] = Entity(surf3)
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

class LevelMuni(Scene):
    def enter(self):

        self.entity_list = []

        self.map = Map('level_muni')
        self.new_layer("background")

        self.current_x = 0
        self.current_y = 0
        self.draw_background()

        

    def draw_background( self ):

        self.remove_all( self.entity_list )
        self.entity_list = []

        x = self.current_x / TILE_SIZE
        y = self.current_y / TILE_SIZE
        x_mod = self.current_x % TILE_SIZE
        y_mod = self.current_y % TILE_SIZE

        for i in range(x,x+TILES_X):
            for j in range(y,y+TILES_Y):
                c = self.map.get_cell(i,j)
                if c is not None:
                    self.entity_list.append( c )
                    self.add("background", c )
                    c.set( left=(i-x)*TILE_SIZE - x_mod, top=(j-y)*TILE_SIZE-y_mod)

    def tick( self ):
        if director.ticker.realtick:
            self.check_keyboard()

    def check_keyboard( self ):
        SKIP_PIXEL = 2
        k = pygame.key.get_pressed()
        if k[K_UP]:
            self.current_y -= SKIP_PIXEL
            if self.current_y < 0:
                self.current_y = 0
        elif k[K_DOWN]:
            self.current_y += SKIP_PIXEL
            if self.current_y > 30 * TILE_SIZE:
                self.current_y = 30 * TILE_SIZE
        if k[K_LEFT]:
            self.current_x -= SKIP_PIXEL
            if self.current_x < 0:
                self.current_x = 0
        elif k[K_RIGHT]:
            self.current_x += SKIP_PIXEL
            if self.current_x > 80 * TILE_SIZE:
                self.current_x = 80 * TILE_SIZE
        if k[K_ESCAPE]:
            director.quit()

        self.draw_background()
