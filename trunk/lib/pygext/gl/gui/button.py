
__all__ = [
    "Button",
    ]

import pygame

from pygext.gl.gui.control import Control
from pygext.gl.director.entities import TextEntity
from pygext.gl.director.globals import director
from pygext.color import _conv_color

from OpenGL.GL import *

class Button(Control):
    def init(self, font, label="Button", fgcolor=(0,0,0), bgcolor=(200,200,200), bevel=2):
        self._entity = None
        self.font = font
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.bevel = bevel
        self.label = label
        self.inverse = False

    def traverse(self):
        root = director.gui_root
        p = pygame.mouse.get_pressed()
        if root.hover is self and p[0]:
            inverse = True
        else:
            inverse = False
        if inverse != self.inverse:
            self.inverse = inverse
        Control.traverse(self)
   
    def execute(self):
        inverse = self.inverse
        bevel = self.bevel
        b = -2*bevel
        r = self.rect.inflate(b,b)
        glDisable(GL_TEXTURE_2D)
        if inverse:
            glColor4f(*self._gl_locolor)
        else:
            glColor4f(*self._gl_hicolor)
        glBegin(GL_QUAD_STRIP)
        glVertex3f(r.left,r.bottom,0)
        glVertex3f(self.left,self.bottom,0)
        glVertex3f(r.left,r.top,0)
        glVertex3f(self.left,self.top,0)
        glVertex3f(r.right,r.top,0)
        glVertex3f(self.right,self.top,0)
        glEnd()
        if not inverse:
            glColor4f(*self._gl_locolor)
        else:
            glColor4f(*self._gl_hicolor)
        glBegin(GL_QUAD_STRIP)
        glVertex3f(r.right,r.top,0)
        glVertex3f(self.right,self.top,0)
        glVertex3f(r.right,r.bottom,0)
        glVertex3f(self.right,self.bottom,0)
        glVertex3f(r.left,r.bottom,0)
        glVertex3f(self.left,self.bottom,0)
        glEnd()
        glColor4f(*self._gl_color)
        glBegin(GL_QUADS)
        glVertex3f(r.left, r.top,0)
        glVertex3f(r.right, r.top,0)
        glVertex3f(r.right, r.bottom,0)
        glVertex3f(r.left, r.bottom,0)
        glEnd()
        glEnable(GL_TEXTURE_2D)
        if self._entity is not None:
            self._entity.centerx = self.centerx
            self._entity.centery = self.centery
            self._entity.traverse()

    def _get_label(self): return self._label
    def _set_label(self, label):
        self._label = label
        if label is None:
            self._entity = None
        else:
            self._entity = TextEntity(self.font, self._label).set(color=self._fgcolor)
    label = property(_get_label, _set_label)

    def _get_fgcolor(self): return self._fgcolor
    def _set_fgcolor(self, color):
        self._fgcolor = color
        if self._entity is not None:
            self._entity.color = color
    fgcolor = property(_get_fgcolor, _set_fgcolor)

    def _get_bgcolor(self): return self._bgcolor
    def _set_bgcolor(self, color):
        self._bgcolor = color
        self._calc_colors()
    bgcolor = property(_get_bgcolor, _set_bgcolor)

    def _calc_colors(self):
        self._gl_color = _conv_color(*self._bgcolor)
        r,g,b,a = self._gl_color
        self._gl_hicolor = r*1.3, g*1.3, b*1.3, a
        self._gl_locolor = r*0.7, g*0.7, b*0.7, a
