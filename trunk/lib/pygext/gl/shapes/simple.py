"""Simple shapes.

This basic shape objects can be used if the Polygon library isn't available.
"""

from pygext.gl.shapes.base import FuncObject
from OpenGL.GL import *
from math import sin,cos,pi

__all__ = [
    "rect",
    "circle",
    ]

def rect(x,y,w,h,color=(1,1,1,1) ):
    return FuncObject(_exec_rect, x, y, w, h, color)

def _exec_rect(x,y,w,h,color):
    glColor4f( color[0],color[1],color[2],color[3] )
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glVertex2f(x,y)
    glVertex2f(x+w,y)
    glVertex2f(x+w,y+h)
    glVertex2f(x,y+h)
    glEnd()
    glEnable(GL_TEXTURE_2D)

def circle(radius, segments=16):
    return FuncObject(_exec_circle, radius, segments)

def _exec_circle(radius, segments):
    glDisable(GL_TEXTURE_2D)
    step = 2*pi/float(segments)
    glBegin(GL_POLYGON)
    for s in range(segments):
        d = step*s
        x = cos(d) * radius
        y = sin(d) * radius
        glVertex2f(x,y)
    glEnd()
    glEnable(GL_TEXTURE_2D)
