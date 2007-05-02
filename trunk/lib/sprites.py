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
from game import Game


class UnicycleEntity(EntityNode):
    layer = "sprites"

    HS_X = 0.5
    HS_Y = 0.73

    def init(self):

        self.load_frames()

        self.move = Move(0,0).do(self)
        self.turn = Rotate(0).do(self)

        self.add_collnode("unicycle", 30,-10,40)
        self.x = 150
        self.y = 300

        self.ticker = 0
        self.on_floor = False

    def get_bounding_rect( self ):
        return self.frames[ self.frame_shown ].get_bounding_rect()

    def load_frames( self ):
        UNI_SPRITE_X = 80
        UNI_SPRITE_Y = 100

        self.frames = []
        sheet = tiles.SpriteSheet('Unicycle80x100_2.png')
        for y in range(4):
            for x in range(5):
                load_x = x * (UNI_SPRITE_X + 1) + 1
                load_y = y * (UNI_SPRITE_Y + 1) + 1
                self.frames.insert( 0, 
                    Entity(
                        sheet.imgat( (load_x, load_y, UNI_SPRITE_X-1, UNI_SPRITE_Y-14), -1),
                        hotspot=(UnicycleEntity.HS_X, UnicycleEntity.HS_Y) ) )
                self.frames[0].attach_to( self )
                self.frames[0].do( Hide() )

        self.frame_shown = 0          
        self.frames[ self.frame_shown ].do( Show() )


    def tick(self):

        # show correct frame
        x = int( (self.x % 120) / 6 )
        if x != self.frame_shown:
            self.frames[ self.frame_shown ].do( Hide() )
            self.frame_shown = x
            self.frames[ x ].do( Show() )
        
        self.ticker += 1

        x = int( self.x )
        base_y = int( self.y ) + self._get_height() * (1-UnicycleEntity.HS_Y)
        y = (Game.map.h * TILE_SIZE) - base_y
        h,s = Game.map.get_h_and_slope(x)

        self.move.vy += GRAVITY

        if y <= h:

            # free falling
            if self.move.vy > 0:

                # bounce
                self.move.vx =  self.move.vx - (self.move.vy/2) * s
                self.move.vy =  - self.move.vy / 3
                if abs(self.move.vy) < 10:
                    self.move.vy = 0
                    self.on_floor = True

            # climbing
            if self.move.vy == 0:
                self.y -=  h-y

        # always decrese X velocity. should surface be important ?
        if self.move.vx < 0:
            self.move.vx += 5
        elif self.move.vx > 0:
            self.move.vx -= 5

        if self.x < 50:
            self.x = 50
        elif self.x > Game.map.w * TILE_SIZE - 50:
            self.x = Game.map.w * TILE_SIZE -50

        # check vertical collision
        if self.move.vx > 0 and Game.map.is_collision_right( x, y ):
            self.move.vx =- self.move.vx

        if self.move.vx < 0 and Game.map.is_collision_left( x, y ):
            self.move.vx =- self.move.vx


    def ride_left( self ):
        s = Game.map.get_slope( int(self.x) )
        self.move.vx = min( -70 - s * 15, self.move.vx )


    def ride_right( self ):
        s = Game.map.get_slope( int(self.x) )
        self.move.vx = max( 70 - s * 15, self.move.vx )

    def mega_jump( self ):
        if self.turn.anglev == 0:
            self.turn.set_velocity(180)
        else:
            self.turn.set_velocity(0)

    def jump( self ):
        if self.on_floor == True:
            self.on_floor = False
            self.move.vy = - 200
