from pygext.gl.all import *
import os,pygame
from pygame.locals import *

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


class LevelMuni(Scene):

    collengine = RadialCollisions

    def enter(self, game):
        self.game = game
        self.map = Map('level_muni')
        self.new_static("background", 0, camera = True)
        self.new_layer("scores", 10, camera = False)
        self.new_layer("sprites", 15, camera = True)

        self.current_x = 0
        self.current_y = 0

        self.score_init()
        self.sprite_init()

        self.draw_tiles()


    def sprite_init( self ):
        self.uni_sprite = Entity("data/unicycle.png", hotspot=(0,0))
        self.uni_sprite.add_collnode("unicycle",80,75,225)
        self.uni_sprite.set(left=0, top=200).place("sprites")
        self.uni_sprite.do( MoveTo( 1000,100,15, mode=PingPongMode ) )

        self.uni_sprite2 = Entity("data/unicycle.png", hotspot=(0.5,0.5))
        self.uni_sprite2.add_collnode("floor")
        self.uni_sprite2.set(left=700, top=200).place("sprites")
        self.uni_sprite2.do( Scale( 0.5, 0.1 ) )
        self.uni_sprite2.do( Fork( Rotate(45), MoveTo( 0,100,15, mode=PingPongMode ) ) )

    def score_init( self ):
        self.pixel_font = GLFont( pygame.font.Font("data/V5PRC___.ttf",24) )
        self.score_text = TextEntity( self.pixel_font, "" )
        self.score_text.set( centerx = 0, centery = 20, color = (255,255,255,255) )
        self.score_text.place("scores")

        self.pos_text= TextEntity( self.pixel_font, "" )
        self.pos_text.set( centerx = 0, centery = 50, color = (255,255,255,255) )
        self.pos_text.place("scores")


    def draw_tiles( self ):
        for i in range(self.map.w):
            for j in range(self.map.h):
                c = self.map.get_cell(i,j)
                if c is not None:
                    self.add("background", c )
                    c.set( left=i*TILE_SIZE, top=j*TILE_SIZE)

    def tick( self ):
        if director.ticker.realtick:
            self.game.score += 1
            self.check_keyboard()
            self.update_score()

    def update_score( self ):
        self.score_text.set_text("score: %d" % self.game.score )
        self.pos_text.set_text("x: %d, y: %d" % (self.current_x, self.current_y) )

    def check_keyboard( self ):
        SKIP_PIXEL = 3
        k = pygame.key.get_pressed()
        if k[K_UP]:
            self.current_y -= SKIP_PIXEL
            if self.current_y < 0:
                self.current_y = 0
        elif k[K_DOWN]:
            self.current_y += SKIP_PIXEL
            if self.current_y > self.map.h * TILE_SIZE - 480:
                self.current_y = self.map.h * TILE_SIZE - 480
        if k[K_LEFT]:
            self.current_x -= SKIP_PIXEL
            if self.current_x < 0:
                self.current_x = 0
        elif k[K_RIGHT]:
            self.current_x += SKIP_PIXEL
            if self.current_x > self.map.w * TILE_SIZE - 640:
                self.current_x = self.map.w * TILE_SIZE - 640
        if k[K_ESCAPE]:
            director.quit()

        self.offset = (self.current_x, self.current_y)


    def collision_unicycle_floor(self, unicycle, floor):
        print "collision (%d,%d) (%d,%d)" % (unicycle.x, unicycle.y, floor.x,floor.y)
