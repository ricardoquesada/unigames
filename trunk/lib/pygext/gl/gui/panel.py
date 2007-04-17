
__all__ = [
    "Panel",
    "ImagePanel",
    "BorderPanel",
    ]

from OpenGL.GL import *
from pygame import Rect

from pygext.gl.gui.control import *
from pygext.gl.gui.utils import *
from pygext.color import _conv_color
from pygext.gl.director.entities import Entity
from pygext.gl.shapes.pattern import PatternImage

import sys
from os.path import join

class Panel(Control):
    def init(self, color=(200,200,200), bevel=True):
        self.color = color
        self.bevel = bevel

    def execute(self):
        glDisable(GL_TEXTURE_2D)
        draw_rect(self.rect, self._gl_color)
        glColor4f(*self._gl_color)
        r = self.rect
        glBegin(GL_QUADS)
        glVertex3f(r.left, r.top,0)
        glVertex3f(r.right, r.top,0)
        glVertex3f(r.right, r.bottom,0)
        glVertex3f(r.left, r.bottom,0)
        glEnd()
        if self.bevel:
            glColor4f(*self._gl_hicolor)
            glBegin(GL_LINE_STRIP)
            glVertex3f(r.left, r.bottom,0)
            glVertex3f(r.left, r.top,0)
            glVertex3f(r.right, r.top,0)
            glEnd()
            glColor4f(*self._gl_locolor)
            glBegin(GL_LINE_STRIP)
            glVertex3f(r.right, r.top,0)
            glVertex3f(r.right, r.bottom,0)
            glVertex3f(r.left, r.bottom,0)
            glEnd()            
        glEnable(GL_TEXTURE_2D)

    def _calc_colors(self):
        self._gl_color = _conv_color(*self.color)
        r,g,b,a = self._gl_color
        self._gl_hicolor = r*1.3,g*1.3,b*1.3,a
        self._gl_locolor = r*0.7,g*0.7,b*0.7,a

    def _get_color(self): return self._color
    def _set_color(self, color):
        self._color = color
        self._calc_colors()
    color = property(_get_color,_set_color)

class ImagePanel(Control):
    def init(self, image=None):
        self.image = image

    def execute(self):
        if self._image is None:
            return
        self._image.set(left=self.left, top=self.top)
        self._image.traverse()

    def _get_image(self): return self._image
    def _set_image(self, image):
        if image is None:
            self._image = None
            self.rect = Rect(0,0,0,0)
        else:
            e = Entity(image)
            self._image = e
            e.set(left=self.left, top=self.top)
            self.rect = e.get_bounding_rect()
    image = property(_get_image, _set_image)

ATTRS = [
    "top",
    "bottom",
    "left",
    "right",
    "topleft",
    "topright",
    "bottomleft",
    "bottomright",
    ]

class _Images(object): pass

class BorderPanel(Control):
    def init(self, bgcolor=(200,200,200), bgfront=False, bgoffset=0, outside=False):
        self.bgcolor = bgcolor
        self.bgfront = bgfront
        self.bgoffset = bgoffset
        self.outside = outside
        self.images = _Images()

    def set_images(self, **kw):
        for a in ATTRS:
            img = PatternImage(kw[a], hotspot=(0,0))
            setattr(self.images, a, img)

    def extract_borders(self, img, (w,h)):
        s = PatternImage._load_surf(img)
        sr = s.get_rect()
        i = self.images
        r = Rect(0,0,w,h)
        def f():
            return PatternImage(s.subsurface(r), hotspot=(0,0))
        i.topleft = f()
        r.right = sr.right
        i.topright = f()
        r.bottom = sr.bottom
        i.bottomright = f()
        r.left = sr.left
        i.bottomleft = f()
        r = Rect(0,h+1,w,4)
        i.left = f()
        r.right = sr.right
        i.right = f()
        r = Rect(w+1,0,4,h)
        i.top = f()
        r.bottom = sr.bottom
        i.bottom = f()

    def execute(self):
        glc = _conv_color(*self.bgcolor)
        r = self.rect
        b = self.bgoffset
        if type(b) is tuple:
            br = r.inflate(b[0]*-2,b[1]*-2)
        else:
            b *= -2
            br = r.inflate(b,b)
        if not self.bgfront:
            draw_rect(br, glc)
        i = self.images
        if self.outside:
            i.topleft.rect.bottomright = r.topleft
            i.topright.rect.bottomleft = r.topright
            i.bottomleft.rect.topright = r.bottomleft
            i.bottomright.rect.topleft = r.bottomright
            i.top.rect.bottomleft = r.topleft
            i.top.rect.width = r.width
            i.bottom.rect.topleft = r.bottomleft
            i.bottom.rect.width = r.width
            i.left.rect.topright = r.topleft
            i.left.rect.height = r.height
            i.right.rect.topleft = r.topright
            i.right.rect.height = r.height
        else:
            i.topleft.rect.topleft = r.topleft
            i.topright.rect.topright = r.topright
            i.bottomleft.rect.bottomleft = r.bottomleft
            i.bottomright.rect.bottomright = r.bottomright
            i.top.rect.topleft = i.topleft.rect.topright
            i.top.rect.width = r.width - i.topleft.rect.width - i.topright.rect.width
            i.bottom.rect.bottomleft = i.bottomleft.rect.bottomright
            i.bottom.rect.width = r.width - i.bottomleft.rect.width - i.bottomright.rect.width
            i.left.rect.topleft = i.topleft.rect.bottomleft
            i.left.rect.height = r.height - i.topleft.rect.height - i.bottomleft.rect.height
            i.right.rect.topright = i.topright.rect.bottomright
            i.right.rect.height = r.height - i.topright.rect.height - i.bottomright.rect.height
        glColor4f(1,1,1,1)
        for a in ATTRS:
            getattr(i, a)._execute()
        if self.bgfront:
            draw_rect(br, glc)
        
