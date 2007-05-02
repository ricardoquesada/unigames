from config import *
from pygext.gl.all import *
import pygame
import sound
from pygame.locals import *
import tiles 
from tiles import TILE_SIZE
from sprites import UnicycleEntity
from pygext.lazy import Random
from pygext.gl.shapes.simple import rect
from game import Game

class LevelMuni(Scene):

    collengine = RadialCollisions

    def enter(self, game):
        self.game = game
#        Game.map = tiles.WfxMap('level_muni_1.tga')
#        Game.map = tiles.OldMap('level_muni.bmp')
        Game.map = tiles.DownHillMap( map_name = 'level_muni_2.tga', sprite_sheet = 'tiles_2.png')
        self.new_layer("particles", 20, camera = True)
        self.new_layer("sprites", 15, camera = True)
        self.new_layer("score_panel", 10, camera = False)
        self.new_layer("score_panel_alpha", 9, camera = False)
        self.new_static("tiles", 0, camera = True)
        self.new_static("sky",-10)

        self.current_x = 0
        self.current_y = 0

        self.score_init()
        self.sky_init()
        self.sprite_init()

        self.draw_tiles()
        self.music_init()

    def music_init( self ):
        sound.init_music()
        sound.play_song("crikey_introtheme.mod")

    def sprite_init( self ):
        self.uni_sprite = UnicycleEntity()

    def score_init( self ):
        self.pixel_font = GLFont( pygame.font.Font("data/V5PRC___.ttf",19) )
        self.score_text = TextEntity( self.pixel_font, "" )
        self.score_text.set( centerx = 0, centery = 20, color = (255,255,255,255) )
        self.score_text.place("score_panel")

        self.pos_text= TextEntity( self.pixel_font, "" )
        self.pos_text.set( centerx = 0, centery = 50, color = (255,255,255,255) )
        self.pos_text.place("score_panel")

        self.power_bar = Entity("data/power_bar.png")
        self.power_bar.set( centerx = SCREEN_RES_X /2, centery = 20 )
        self.power_bar.place("score_panel")

        self.unicycle_lifes = [ Entity("data/unicycle_life.png"),Entity("data/unicycle_life.png"),Entity("data/unicycle_life.png") ]
        for i,e in enumerate(self.unicycle_lifes):
            e.set( centerx = 560 + i * (e.width+3), centery = 20 )
            e.place("score_panel")

        bar_alpha = rect(0,0,SCREEN_RES_X,40, (0,0,0,0.6) )
        self.bar_alpha = Entity(bar_alpha).place("score_panel_alpha")

    def sky_init( self ):
#        gr = GradientRect(SCREEN_RES_X,SCREEN_RES_Y + SKY_LIMIT)
#        gr.set_colors( top=(0,0,0,255), bottom=(32,32,128,255),)
#        self.sky = Entity(gr).place("sky").set( y=-SKY_LIMIT, x=0,)
        self.sky = Entity("data/background_0.png").place("sky")
        self.sky.set(centerx=SCREEN_RES_X/2,centery=SCREEN_RES_Y/2)


    def draw_tiles( self ):
        for i in range(Game.map.w):
            for j in range(Game.map.h):
                c = Game.map.get_cell(i,j)
                if c is not None:
                    self.add("tiles", c )
                    c.set( left=i*TILE_SIZE, top=j*TILE_SIZE)


    def tick(self):
        # sky limit
        cx = self.uni_sprite.x - SCREEN_RES_X / 2
        cy = self.uni_sprite.y - SCREEN_RES_Y / 2
        if cy < -SKY_LIMIT:
            cy = -SKY_LIMIT
        elif cy > 0:
            cy /= 1.5
        if cx < 0:
            cx = 0
        if cx > Game.map.w * TILE_SIZE:
            cx = Game.map.w * TILE_SIZE

        # camera location
        self.offset = (cx,cy)
#        self.sky.y = (SKY_LIMIT + cy) * -0.5

    def realtick( self ):
        if director.ticker.realtick:
            self.game.score += 1
            self.check_keyboard()
            self.update_score()
            self.uni_sprite.tick()

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
       
        if k[K_SPACE]:
            self.uni_sprite.mega_jump()

        if k[K_ESCAPE]:
            director.quit()
        
    def collision_unicycle_floor(self, unicycle, floor):
        print "collision (%d,%d) (%d,%d)" % (unicycle.x, unicycle.y, floor.x,floor.y)
