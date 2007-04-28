from pygext.gl.all import *
import pygame
from pygame.locals import *
import map
from map import TILE_SIZE
from sprites import UnicycleEntity
from pygext.lazy import Random

from pygext.gl.shapes.simple import rect

SKY_LIMIT = 100


class LevelMuni(Scene):

    collengine = RadialCollisions

    def enter(self, game):
        self.game = game
        self.map = map.Map('level_muni')
        self.new_static("background", 0, camera = True)
        self.new_layer("dirt", 20, camera = True)
        self.new_layer("scores", 10, camera = False)
        self.new_layer("scores-alpha", 9, camera = False)
        self.new_layer("sprites", 15, camera = True)
        self.new_layer("sky",-10)

        self.current_x = 0
        self.current_y = 0

        self.score_init()
        self.sky_init()
        self.sprite_init()
        self.particle_system_init()

        self.draw_tiles()

    def particle_system_init( self ):
        self.particle_system = DirtSystem()

    def sprite_init( self ):
        self.uni_sprite = UnicycleEntity()

    def score_init( self ):
        self.pixel_font = GLFont( pygame.font.Font("data/V5PRC___.ttf",19) )
        self.score_text = TextEntity( self.pixel_font, "" )
        self.score_text.set( centerx = 0, centery = 20, color = (255,255,255,255) )
        self.score_text.place("scores")

        self.pos_text= TextEntity( self.pixel_font, "" )
        self.pos_text.set( centerx = 0, centery = 50, color = (255,255,255,255) )
        self.pos_text.place("scores")

        self.power_bar = Entity("data/power_bar.png")
        self.power_bar.set( centerx = 320, centery = 20 )
        self.power_bar.place("scores")

        bar_alpha = rect(0,0,640,40,
                    (0.2,0.2,0.2,0.6) )
        bar_alpha.alpha( 32 )
        bar_alpha.compile()
        self.bar_alpha = Entity(bar_alpha).place("scores-alpha")

    def sky_init( self ):
        gr = GradientRect(640,480 + SKY_LIMIT)
        gr.set_colors(
            top=(0,0,0,255),
            bottom=(64,64,128,255),
            )
        self.sky = Entity(gr).place("sky").set(
            y=-SKY_LIMIT,
            x=0,
            )


    def draw_tiles( self ):
        for i in range(self.map.w):
            for j in range(self.map.h):
                c = self.map.get_cell(i,j)
                if c is not None:
                    self.add("background", c )
                    c.set( left=i*TILE_SIZE, top=j*TILE_SIZE)


    def tick(self):
        # sky limit
        cx = self.uni_sprite.x - 320
        cy = self.uni_sprite.y - 240
        if cy < -SKY_LIMIT:
            cy = -SKY_LIMIT
        elif cy > 0:
            cy = 0
        if cx < 0:
            cx = 0
        if cx > 3000:
            cx = 3000

        # camera location
        self.offset = (cx,cy)

        self.sky.y = (SKY_LIMIT + cy) * -0.5

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
            self.particle_system.new_emitter( CrashEmitter, x=self.uni_sprite.x, y=self.uni_sprite.y+50 )
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


class CrashEmitter(CircleEmitter):
    tangent = False
    radius = 20
    
    direction = 0
    angle = 160
    velocity = Random(10, 150)
    num_particles = 20
    num_emits = 1
    scale = Random(0.5,1.0)
    rotation = Random(360)
    rotation_delta = Random(-150,150)
    life = Random(0.5,2)
    fade_time = 0.1


class DirtSystem(BitmapParticleSystem):
    image = "data/dirtparticle.png"
    layer = "dirt"
    mutators = [
        LinearForce(0,200),
        ]
