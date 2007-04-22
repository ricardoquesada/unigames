from pygext.gl.all import *
import os,pygame
from pygame.locals import *

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

        self.bg = {}
        img = load_image(mapname + '.bmp')
        self.w, self.h = img.get_width(),img.get_height()
        for j in range(0, self.h):
            # flip vertically
            fj = self.h - j - 1
            for i in range(0, self.w):
                print "loading (%d,%d)" % (i,j)
                cell = img.get_at((i, j))
                if cell == (0,0,0,255):
                    self.bg[ (i,j) ] = Entity(surf)
                else:
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

        for i in range(self.current_x,self.current_x+30):
            for j in range(self.current_y,self.current_y+30):
                c = self.map.get_cell(i,j)
                if c is not None:
                    self.entity_list.append( c )
                    self.add("background", c )
                    c.set( left=(i-self.current_x)*32, top=(j-self.current_y)*32).place('background')

    def handle_keydown(self, ev):
        # press any key to rotate the Entities around their hotspot
        if ev.key == K_UP:
            self.current_y -= 1
            if self.current_y < 0:
                self.current_y = 0
        elif ev.key == K_DOWN:
            self.current_y += 1
            if self.current_y > 30:
                self.current_y = 30 
        elif ev.key == K_LEFT:
            self.current_x -= 1
            if self.current_x < 0:
                self.current_x = 0
        elif ev.key == K_RIGHT:
            self.current_x += 1
            if self.current_x > 30:
                self.current_x = 30 
        elif ev.key == K_ESCAPE:
            director.quit()

        print self.current_x, self.current_y
        self.draw_background()
