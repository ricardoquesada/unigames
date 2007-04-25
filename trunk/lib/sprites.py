try:
    from psyco.classes import *
except ImportError:
    pass

from pygext.gl.all import *
from pygext.math.vecalg import sincos
from pygext.render.stencils import alpha_stencil
from pygext.lazy import Random

from map import TILE_SIZE


class UnicycleEntity(EntityNode):
    image = "data/unicycle.png"
    layer = "sprites"

    def init(self):
        s = Bitmap._load_surf(self.image)
        s = alpha_stencil(s)
        s = Entity(s)
        s.attach_to(self)
        s.alpha = 0

        self.stencil = s

        self.move = Move(0,0).do(self)
        self.turn = Rotate(0).do(self)

        self.add_collnode("unicycle", 30,-10,40)
        self.centerx = 150
        self.centery = 300

        self.ticker = 0
        self.jumping = False
        self.on_floor = False


    def flash(self):
        self.stencil.abort_actions(ColorFade)
        self.stencil.color = (255,100,100,150)
        self.stencil.do(ColorFade((50,0,0,0), secs=0.5))

    def tick(self, map):

        self.ticker += 1

        if self.jumping == False:
            x = int( self.x )
            y = int( self.y ) + self._get_height() / 2
            y = (map.h * TILE_SIZE) - y
            h = map.get_h(x)

            if y > h:
                self.move.add_velocity(0, 5)
            else:
                self.move.vy = 0
                self.on_floor = True

        else:
            self.move.vy *= 0.9
            if self.move.vy > -10:
                self.move.vy = 0
                self.jumping = False

        if self.move.vx < 0:
            self.move.vx += 1
        elif self.move.vx > 0:
            self.move.vx -= 1

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
