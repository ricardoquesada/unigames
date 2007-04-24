from pygext.gl.all import *
import pygame
from pygame.locals import *
import map
from map import TILE_SIZE
from sprites import UnicycleEntity


class LevelMuni(Scene):

    collengine = RadialCollisions

    def enter(self, game):
        self.game = game
        self.map = map.Map('level_muni')
        self.new_static("background", 0, camera = True)
        self.new_layer("scores", 10, camera = False)
        self.new_layer("sprites", 15, camera = True)

        self.current_x = 0
        self.current_y = 0

        self.score_init()
        self.sprite_init()

        self.draw_tiles()


    def sprite_init( self ):
        self.uni_sprite = UnicycleEntity()

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


    def tick(self):
        # sky limit
        sh = 1200
        cx = self.uni_sprite.x - 320
        cy = self.uni_sprite.y - 240
        if cy < -sh:
            cy = -sh
        elif cy > 0:
            cy = 0
        if cx < 0:
            cx = 0
        if cx > 3000:
            cx = 3000

        # camera location
        self.offset = (cx,cy)


    def realtick( self ):
        if director.ticker.realtick:
            self.game.score += 1
            self.check_keyboard()
            self.update_score()
            self.uni_sprite.tick( self.map )

    def update_score( self ):
        self.score_text.set_text("score: %d" % self.game.score )
        self.pos_text.set_text("x: %d, y: %d" % (self.uni_sprite.x, self.uni_sprite.y) )

    def check_keyboard( self ):
        k = pygame.key.get_pressed()
        if k[K_UP]:
            self.uni_sprite.jump()
        elif k[K_DOWN]:
            pass
        if k[K_LEFT]:
            self.uni_sprite.ride_left()
        elif k[K_RIGHT]:
            self.uni_sprite.ride_right()
        if k[K_ESCAPE]:
            director.quit()

    def collision_unicycle_floor(self, unicycle, floor):
        print "collision (%d,%d) (%d,%d)" % (unicycle.x, unicycle.y, floor.x,floor.y)
