
## XXX: refactor emit method so that there can be more reuse and less copy/paste

__all__ = [
    "BaseEmitter",
    "PointEmitter",
    "LineEmitter",
    "RectEmitter",
    "CircleEmitter",
    "RingEmitter",
    ]

try:
    from psyco.classes import *
except:
    pass


from pygext.gl.director.actions import Delay,CallFunc
from pygext.gl.director.globals import director
from pygext.color import _conv_color

from pygext.gl.particles.python_impl.particle import Particle
from pygext.math.vecalg import *

from random import random
from math import pi,sin,cos

class BaseEmitter(object):
    delay = 0.1
    num_particles = 1
    num_emits = None
    life = 1
    fade_time = 1
    fade_in = 0
    color = (255,255,255,255)
    rotation = 0
    rotation_delta = 0
    scale = 1.0
    scale_delta = 0.0
    align_to_node = True
    align_rotation = False

    collision_radius = None
    collision_group = None

    direction = 0
    angle = 360
    velocity = 100
    offset = 0

    even_spread = False

    def __init__(self, system, node=None, x=0, y=0):
        self.node = node
        self.static_pos = x,y
        self.system = system
        self.emits = self.num_emits
        self.init()

    def init(self):
        pass

    def start(self):
        if self.delay is not None:
            d = float(self.delay) * random()
            act = Delay(d) + CallFunc(self._emit)
            act.do()
        else:
            self.emit()
            

    def _emit(self):
        if self.emits is None and self.node.deleted:
            return
        self.emit()
        d = float(self.delay)
        if self.emits is not None:
            self.emits -= 1
            if self.emits <= 0:
                return
        act = Delay(d) + CallFunc(self._emit)
        act.do()
        
    def emit(self):
        node = self.node
        if node is None:
            rx,ry = self.static_pos
        else:
            rx,ry = node.realx,node.realy
        ang = self.angle
        ang2 = ang/2.0
        scene = director.scene
        num = int(self.num_particles)
        if self.even_spread:
            if num == 1:
                dir = float(self.direction)
                dir_delta = 0
            else:
                spread_ang = float(self.angle)
                dir = float(self.direction) - spread_ang / 2.0
                dir_delta = spread_ang / float(num-1)
        for n in xrange(num):
            p = Particle()
            p.x = rx
            p.y = ry
            p.rotation = float(self.rotation)
            p.scale = float(self.scale)
            p.rotationd = float(self.rotation_delta)
            p.scaled = float(self.scale_delta)
            p.fade_in = float(self.fade_in)
            if self.even_spread:
                angle = dir + dir_delta * n
            else:
                angle = float(self.direction) + random()*ang - ang2
            if self.align_to_node and node:
                angle += node.angle
            if self.align_rotation:
                p.rotation += angle
            angle = pi * angle / 180.0 + pi
            v = float(self.velocity)
            o = float(self.offset)
            dx = -sin(angle)
            dy = cos(angle)
            if o:
                p.x += dx * o
                p.y += dy * o
            p.vx = dx * v
            p.vy = dy * v
            p.life = float(self.life)
            p.fade_time = float(self.fade_time)
            p.color = _conv_color(*map(float,self.color))
            g = self.collision_group
            if g is not None:
                c = self.collision_radius
                c = int(c)
                p.collnode = scene.coll.add_node(g, p, c)
            self.system.add_particle(p)
            self._tweak(p)
            p.emitter = self

    def _tweak(self, p):
        pass


class PointEmitter(BaseEmitter):
    pass


class LineEmitter(BaseEmitter):
    direction = 0
    angle = 0
    tangent = True

    start_point = (-50,0)
    end_point = (50,0)

    def _tweak(self, p):
        loc = random()
        loci = 1-loc
        sx,sy = map(float, self.start_point)
        ex,ey = map(float, self.end_point)
        p.x += sx*loc + ex*loci
        p.y += sy*loc + ey*loci

    def init(self):
        v = vec(*self.end_point)-vec(*self.start_point)
        v = ortho(v)
        self.tdir = direction(v)

    def emit(self):
        node = self.node
        if node is None:
            rx,ry = self.static_pos
        else:
            rx,ry = node.realx,node.realy
        ang = self.angle
        ang2 = ang/2.0
        
        num = int(self.num_particles)
        if self.even_spread:
            if num == 1:
                dir = float(self.direction)
                dir_delta = 0
            else:
                spread_ang = float(self.angle)
                dir = float(self.direction) - spread_ang / 2.0
                dir_delta = spread_ang / float(num-1)
        for n in xrange(int(self.num_particles)):
            p = Particle()
            p.x = rx
            p.y = ry
            p.rotation = float(self.rotation)
            p.scale = float(self.scale)
            p.rotationd = float(self.rotation_delta)
            p.scaled = float(self.scale_delta)
            p.fade_in = float(self.fade_in)
            if self.even_spread:
                angle = dir + dir_delta * n
            else:
                angle = float(self.direction) + random()*ang - ang2
            if self.align_to_node and node:
                angle += node.angle
            if self.tangent:
                angle += self.tdir
            if self.align_rotation:
                p.rotation += angle
            angle = pi * angle / 180.0 + pi
            v = float(self.velocity)
            o = float(self.offset)
            dx = -sin(angle)
            dy = cos(angle)
            if o:
                p.x += dx * o
                p.y += dy * o
            p.vx = dx * v
            p.vy = dy * v
            p.life = float(self.life)
            p.fade_time = float(self.fade_time)
            p.color = _conv_color(*map(float,self.color))
            self.system.add_particle(p)
            self._tweak(p)
            p.emitter = self


class RectEmitter(BaseEmitter):
    rect = (-50,-50,50,50)

    def _tweak(self, p):
        xloc = random()
        xloci = 1-xloc
        yloc = random()
        yloci = 1-yloc
        sx,sy = map(float, self.rect[:2])
        ex,ey = map(float, self.rect[2:])
        p.x += sx*xloc + ex*xloci
        p.y += sy*yloc + ey*yloci

class CircleEmitter(BaseEmitter):
    radius = 50
    tangent = True
    angle = 0
    direction = 0

            
    def emit(self):
        node = self.node
        if node is None:
            rx,ry = self.static_pos
        else:
            rx,ry = node.realx,node.realy
        ang = self.angle
        ang2 = ang/2.0
        
        num = int(self.num_particles)
        if self.even_spread:
            if num == 1:
                dir = float(self.direction)
                dir_delta = 0
            else:
                spread_ang = float(self.angle)
                dir = float(self.direction) - spread_ang / 2.0
                dir_delta = spread_ang / float(num-1)
        for n in xrange(int(self.num_particles)):
            p = Particle()
            p.x = rx
            p.y = ry
            p.rotation = float(self.rotation)
            p.scale = float(self.scale)
            p.rotationd = float(self.rotation_delta)
            p.scaled = float(self.scale_delta)
            p.fade_in = float(self.fade_in)
            posangle = random()*360
            posrad = random()*float(self.radius)
            radians = pi * posangle/180.0 + pi
            p.x += -sin(radians) * posrad
            p.y += cos(radians) * posrad
            
            if self.even_spread:
                angle = dir + dir_delta * n
            else:
                angle = float(self.direction) + random()*ang - ang2
            if self.align_to_node and node:
                angle += node.angle
            if self.tangent:
                angle += posangle
            if self.align_rotation:
                p.rotation += angle
            angle = pi * angle / 180.0 + pi
            v = float(self.velocity)
            o = float(self.offset)
            dx = -sin(angle)
            dy = cos(angle)
            if o:
                p.x += dx * o
                p.y += dy * o
            p.vx = dx * v
            p.vy = dy * v
            p.life = float(self.life)
            p.fade_time = float(self.fade_time)
            p.color = _conv_color(*map(float,self.color))
            self.system.add_particle(p)
            self._tweak(p)
            p.emitter = self

class RingEmitter(CircleEmitter):

    def emit(self):
        node = self.node
        if node is None:
            rx,ry = self.static_pos
        else:
            rx,ry = node.realx,node.realy
        ang = self.angle
        ang2 = ang/2.0
        
        num = int(self.num_particles)
        if self.even_spread:
            if num == 1:
                dir = float(self.direction)
                dir_delta = 0
            else:
                spread_ang = float(self.angle)
                dir = float(self.direction) - spread_ang / 2.0
                dir_delta = spread_ang / float(num-1)
        for n in xrange(int(self.num_particles)):
            p = Particle()
            p.x = rx
            p.y = ry
            p.rotation = float(self.rotation)
            p.scale = float(self.scale)
            p.rotationd = float(self.rotation_delta)
            p.scaled = float(self.scale_delta)
            p.fade_in = float(self.fade_in)
            posangle = random()*360
            posrad = float(self.radius)
            radians = pi * posangle/180.0 + pi
            p.x += -sin(radians) * posrad
            p.y += cos(radians) * posrad
            
            if self.even_spread:
                angle = dir + dir_delta * n
            else:
                angle = float(self.direction) + random()*ang - ang2
            if self.align_to_node and node:
                angle += node.angle
            if self.tangent:
                angle += posangle
            if self.align_rotation:
                p.rotation += angle
            angle = pi * angle / 180.0 + pi
            v = float(self.velocity)
            o = float(self.offset)
            dx = -sin(angle)
            dy = cos(angle)
            if o:
                p.x += dx * o
                p.y += dy * o
            p.vx = dx * v
            p.vy = dy * v
            p.life = float(self.life)
            p.fade_time = float(self.fade_time)
            p.color = _conv_color(*map(float,self.color))
            self.system.add_particle(p)
            self._tweak(p)
            p.emitter = self
