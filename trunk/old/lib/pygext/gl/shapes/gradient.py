
__all__ = [
    "GradientRect",
    ]

from pygext.gl.shapes.base import GLShape
from pygext.color import _conv_color

from OpenGL.GL import *

class GradientRect(GLShape):
    def init(self, width, height, hotspot=(0,0)):
        self.width = width
        self.height = height
        self.hotspot = hotspot
        self.topleft = (0,0,0,0)
        self.topright = (0,0,0,0)
        self.bottomleft = (0,0,0,0)
        self.bottomright = (0,0,0,0)

    def set_colors(self, topleft=None, topright=None, bottomleft=None, bottomright=None,
                   top=None, bottom=None,left=None, right=None):
        if topleft is not None:
            self.topleft = _conv_color(*topleft)
        if topright is not None:
            self.topright = _conv_color(*topright)
        if bottomleft is not None:
            self.bottomleft = _conv_color(*bottomleft)
        if bottomright is not None:
            self.bottomright = _conv_color(*bottomright)
        if top is not None:
            self.topleft = _conv_color(*top)
            self.topright = _conv_color(*top)
        if bottom is not None:
            self.bottomleft = _conv_color(*bottom)
            self.bottomright = _conv_color(*bottom)
        if left is not None:
            self.topleft = _conv_color(*left)
            self.bottomleft = _conv_color(*left)
        if right is not None:
            self.topright = _conv_color(*right)
            self.bottomright = _conv_color(*right)
        self.unallocate()
            
    def _execute(self):
        hx,hy = self.hotspot
        x = -hx * self.width
        y = -hy * self.height
        xx = x + self.width
        yy = y + self.height
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glColor4f(*self.topleft)
        glVertex3f(x,y,0)
        glColor4f(*self.topright)
        glVertex3f(xx,y,0)
        glColor4f(*self.bottomright)
        glVertex3f(xx,yy,0)
        glColor4f(*self.bottomleft)
        glVertex3f(x,yy,0)
        glEnd()
        glEnable(GL_TEXTURE_2D)
