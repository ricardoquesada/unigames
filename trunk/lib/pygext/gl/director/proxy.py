
__all__ = [
    "EntityProxy",
    ]

from pygext.gl.director.entities import Entity
from OpenGL.GL import glPushMatrix, glPopMatrix

class EntityProxy(Entity):
    fast_draw = False
    
    def __init__(self, entity):
        Entity.__init__(self)
        self.entity = entity
        
    def enter(self):
        glPushMatrix()
        self.entity._draw_here()
        glPopMatrix()
