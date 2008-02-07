
__all__ = [
    "ParticleSystem",
    "PointParticleSystem",
    "BitmapParticleSystem",
    "SimpleBitmapParticleSystem",
    "HaloBitmapParticleSystem",
    ]

try:
    from psyco.classes import *
except:
    pass

try:
    Set = set
except:
    from sets import Set

from OpenGL.GL import *
from pygext.gl.director.globals import director
from pygext.gl.shapes.bitmap import Bitmap
from pygext.gl.director.entities import Entity
from pygame.time import get_ticks

class ParticleSystem(object):
    mutators = []

    fast_draw = False
    layer = None

    def __init__(self):
        self.particles = Set()
        if self.layer is not None:
            self.place(self.layer)
        self.init()

    def init(self):
        pass

    def traverse(self):
        pass

    def add_particle(self, particle):
        self.particles.add(particle)

    def new_emitter(self, cls, node=None, x=0, y=0):
        emitter = cls(self, node, x, y)
        emitter.start()

    def place(self, layer):
        director.scene.layers[layer][1]._attach(self)

    def _delete(self):
        self.particles = None

class PointParticleSystem(ParticleSystem):
    pass	

class BitmapParticleSystem(ParticleSystem):
    image = None
    hotspot = (0.5,0.5)

    def init(self):
        image = self.image
        if not isinstance(image, Bitmap):
            image = Entity(image, hotspot=self.hotspot).shape        
        image.compile()
        self.texid = image._tex.texid
        self.listid = glGenLists(1)
        glNewList(self.listid, GL_COMPILE)
        image._particle_execute()
        glEndList()
        self.prevtick = get_ticks()

    def traverse(self,
                 glColor4f=glColor4f,
                 glPushMatrix=glPushMatrix,
                 glTranslatef=glTranslatef,
                 glRotatef=glRotatef,
                 glScalef=glScalef,
                 glCallList=glCallList,
                 glPopMatrix=glPopMatrix):
        delta = director.ticker.tick_delta
        glBindTexture(GL_TEXTURE_2D, self.texid)
        deleted = []

        for p in self.particles:
            p.life -= delta
            if p.life <= 0:
               deleted.append(p)
               continue
            p.age += delta

            p.x += p.vx * delta
            p.y += p.vy * delta
            p.scale += p.scaled * delta
            p.rotation += p.rotationd * delta

            node = p.collnode
            if node is not None:
                node.realx = p.x
                node.realy = p.y

            r,g,b,a = p.color
            if p.age < p.fade_in:
                a *= (p.age/p.fade_in)
            if p.life < p.fade_time:
                a *= (p.life/p.fade_time)
                
            glColor4f(r,g,b,a)
            glPushMatrix()
            glTranslatef(p.x,p.y,0)
            glRotatef(p.rotation,0,0,1)
            glScalef(p.scale,p.scale,0)
            glCallList(self.listid)
            glPopMatrix()
        for p in deleted:
            self.particles.remove(p)
        for m in self.mutators:
            m.mutate(self.particles, delta)
            
    def __del__(self):
        glDeleteLists(self.listid, 1)

class HaloBitmapParticleSystem(BitmapParticleSystem):

    alpha = 0.1
    scale = 1.5
    
    def init(self, srcsystem):
        self.src = srcsystem

    def traverse(self,
                 glColor4f=glColor4f,
                 glPushMatrix=glPushMatrix,
                 glTranslatef=glTranslatef,
                 glRotatef=glRotatef,
                 glScalef=glScalef,
                 glCallList=glCallList,
                 glPopMatrix=glPopMatrix):
        glBindTexture(GL_TEXTURE_2D, self.texid)

        for p in self.src.particles:

            r,g,b,a = p.color
            if p.age < p.fade_in:
                a *= (p.age/p.fade_in)
            if p.life < p.fade_time:
                a *= (p.life/p.fade_time)
            a *= self.alpha
            scale = p.scale * self.scale
                
            glColor4f(r,g,b,a)
            glPushMatrix()
            glTranslatef(p.x,p.y,0)
            glRotatef(p.rotation,0,0,1)
            glScalef(scale,scale,0)
            glCallList(self.listid)
            glPopMatrix()
    

class SimpleBitmapParticleSystem(BitmapParticleSystem):
    
    def traverse(self):
        delta = director.ticker.tick_delta
        glBindTexture(GL_TEXTURE_2D, self.texid)
        deleted = []
        ## TODO: optimize using vertex and color arrays
        for p in self.particles:
            p.life -= delta
            if p.life <= 0:
               deleted.append(p)
               continue
            p.age += delta

            p.x += p.vx * delta
            p.y += p.vy * delta
            p.scale += p.scaled * delta
            p.rotation += p.rotationd * delta

            r,g,b,a = p.color
            if p.age < p.fade_in:
                a *= (p.age/p.fade_in)
            if p.life < p.fade_time:
                a *= (p.life/p.fade_time)
                
            glColor4f(r,g,b,a)
            glTranslatef(p.x,p.y,0)
            glCallList(self.listid)
            glTranslatef(-p.x,-p.y,0)
        for p in deleted:
            self.particles.remove(p)
        for m in self.mutators:
            m.mutate(self.particles, delta)
