try:
    from psyco.classes import *
except ImportError:
    pass

from config import *
from pygext.gl.all import *
from pygext.math.vecalg import sincos
from pygext.render.stencils import alpha_stencil

from tiles import TILE_SIZE
import tiles


class UnicycleEntity(EntityNode):
    image = "data/dirtparticle.png"
    layer = "sprites"

    def init(self):
#        s = Bitmap._load_surf(self.image)
#        s = alpha_stencil(s)
#        s = Entity(s)
#        s.attach_to(self)
#        s.alpha = 0
#        self.stencil = s

        self.load_frames()

        self.move = Move(0,0).do(self)
        self.turn = Rotate(0).do(self)

        self.add_collnode("unicycle", 30,-10,40)
        self.centerx = 150
        self.centery = 300

        self.ticker = 0
        self.jumping = False
        self.on_floor = False

#        self.do( Hide() )

    def load_frames( self ):
        UNI_SPRITE_X = 80
        UNI_SPRITE_Y = 100

        self.frames = []
        sheet = tiles.SpriteSheet('Unicycle80x100_2.png')
        for y in range(4):
            for x in range(5):
                load_x = x * (UNI_SPRITE_X + 1) + 1
                load_y = y * (UNI_SPRITE_Y + 1) + 1
                print "loading from: %d,%d" % ( load_x, load_y  )
                self.frames.insert(0, Entity(sheet.imgat( (load_x, load_y, UNI_SPRITE_X-1, UNI_SPRITE_Y-1), -1)) )
                self.frames[0].attach_to( self )
                self.frames[0].do( Hide() )

        self.frame_shown = 0          
        self.frames[ self.frame_shown ].do( Show() )

    def flash(self):
        self.stencil.abort_actions(ColorFade)
        self.stencil.color = (255,100,100,150)
        self.stencil.do(ColorFade((50,0,0,0), secs=0.5))


    def tick(self, map):

        # show correct frame
        x = int( (self.x % 120) / 6 )
        if x != self.frame_shown:
            self.frames[ self.frame_shown ].do( Hide() )
            self.frame_shown = x
            self.frames[ x ].do( Show() )
            print "frame: %d" % x
        
        self.ticker += 1
        if self.jumping == False:
            x = int( self.x )
            y = int( self.y ) + self._get_height() / 2
            y = (map.h * TILE_SIZE) - y
            h = map.get_h(x)

            if y > h:
                self.move.add_velocity(0, GRAVITY)
            else:
                self.move.vy = 0
                self.on_floor = True

        else:
            self.move.vy *= 0.9
            if self.move.vy > -10:
                self.move.vy = 0
                self.jumping = False

        if self.move.vx < 0:
            self.move.vx += 5
        elif self.move.vx > 0:
            self.move.vx -= 5

        if self.x < 50:
            self.x = 50


    def ride_left( self ):
        self.move.vx = -70

    def ride_right( self ):
        self.move.vx = 70

    def jump( self ):
        if self.on_floor == True and self.jumping == False:
            self.jumping = True
            self.on_floor = False
            self.move.vy = -200
