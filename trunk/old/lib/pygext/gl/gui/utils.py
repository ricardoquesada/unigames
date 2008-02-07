
__all__ = [
    "draw_rect",
    ]

from OpenGL.GL import *

def draw_rect(r, color):
    glDisable(GL_TEXTURE_2D)
    glColor4f(*color)
    glBegin(GL_QUADS)
    glVertex3f(r.left, r.top,0)
    glVertex3f(r.right, r.top,0)
    glVertex3f(r.right, r.bottom,0)
    glVertex3f(r.left, r.bottom,0)
    glEnd()
    glEnable(GL_TEXTURE_2D)
