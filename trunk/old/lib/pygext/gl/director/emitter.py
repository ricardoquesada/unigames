"""Entity Emitter

This utility class is used to automatically generate several entities. It
should be used when you need more features for the generated entities than
what is provided by the pygext.gl.particles package. However, if you need
to generate a large number of particles, the particle package should be
used for better performance.

Features provided by EntityEmitter not supported by pygext.gl.particles:
 * Animated particles
 * Using Entity actions (such as Rotate) for generated particles
 * A callback function that is called for each generated particle
 * Collision nodes for the generated particles
"""

from pygext.gl.director.actions import *
from pygext.gl.director.globals import director
from math import sin,cos,pi
from random import random, choice

__all__ = [
    "EntityEmitter",
    ]

class EntityEmitter(object):
    
    image = None
    anim = None
    animtime = 1
    animmode = RepeatMode
    
    color = (255,255,255,255)

    action = None
    callback = None

    delay = None # how many seconds between emits
    numparticles = 1 # how many particles per emit
    numemits = None # how many emissions (None for unlimited)

    scale = 1.0

    speed = None # pixels per second
    vx = 0
    vy = 0

    x = 0
    y = 0
    
    speedmult = 0 # multiplier for parent node speed

    life = 1.0  # lifetime in seconds
    fade = True
    fadelimit = 0.0 # seconds after which the particle starts fading

    linked = False # will the particles stay linked to the parent node
    layer = None

    collgroup = None
    collradius = 0
    
    def __init__(self, node):
        self.node = node
        if self.numemits is not None:
            self.numemits = int(self.numemits)
        if self.delay is None:
            for i in xrange(int(self.numparticles)):
                self.emit()
        else:
            secs = float(self.delay)
            act = Delay(secs) + CallFunc(self._emit)
            act.do()

    def emit(self):
        if type(self.image) is list:
            image = choice(self.image)
        else:
            image = self.image
        part = Entity(image)
        if self.anim is not None:
            part.do(Animate(self.anim, self.animtime, self.animmode))
        if self.action is not None:
            part.do(self.action)
        if self.linked:
            part.attach_to(self.node)
        elif self.layer is not None:
            part.place(self.layer).set(x=self.node.realx+float(self.x), y=self.node.realy+float(self.y))
        if self.collgroup is not None:
            part.add_collnode(self.collgroup, self.collradius)
        part.scale = float(self.scale)
        part.color = tuple(map(float, self.color))
        if speed is not None:
            angle = random() * 2 * pi
            speed = float(self.speed)
            xx = cos(angle) * speed
            yy = sin(angle) * speed
        else:
            xx = float(self.vx)
            yy = float(self.vy)
        mult = float(self.speedmult)
        if mult:
            moveact = self.node.get_actions(Move)
            if moveact:
                moveact = moveact[0]
                xx += mult * moveact.vx
                yy += mult * moveact.vy
        life = float(self.life)
        act = Move(xx,yy).limit(time=life) + Delete
        part.do(act)
        if self.fade:
            fade = float(self.fadelimit)
            if fade < life:
                if fade > 0:
                    act = Delay(fade) + AlphaFade(0, secs=life-fade)
                else:
                    act = AlphaFade(0, secs=life)
                part.do(act)
        if self.callback is not None:
            self.callback(part)
        
    def _emit(self):
        if self.node.deleted:
            self.node = None
            return
        for i in xrange(int(self.numparticles)):
            self.emit()
        secs = float(self.delay)
        if self.numemits is not None:
            self.numemits -= 1
            if self.numemits == 0:
                return
        act = Delay(secs) + CallFunc(self._emit)
        act.do()
