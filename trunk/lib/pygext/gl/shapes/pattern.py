
__all__ = [
    "PatternImage",
    "Pattern",
    ]

import pygame
from pygame.locals import *
from OpenGL.GL import *

from pygext.gl.shapes.bitmap import Bitmap, power2, _Texture

class Pattern(object):
    pass # holder for the texture

class PatternImage(Bitmap):

    def init(self, img, xsize=None, ysize=None, hotspot=(0,0)):
        Bitmap.init(self, img, hotspot)
        xs,ys = self.size
        if xsize is None:
            xsize = xs
        if ysize is None:
            ysize = ys
        hx,hy = hotspot
        self.rect = Rect(-hx*xsize,-hy*ysize,xsize,ysize)

    def set_hotspot(self, rx, ry):
        self.hotspot = (rx,ry)
        self.unallocate()
        self.rect.left = -rx*self.rect.width
        self.rect.top = -ry*self.rect.height
        return self

    def set_size(self, width=None, height=None):
        if width is not None:
            self.rect.width = width
        if height is not None:
            self.rect.height = height
        hx,hy = self.hotspot
        self.rect.left = -hx*self.rect.width
        self.rect.top = -hy*self.rect.height
        self.unallocate()

    def _setimage(self, img):
        xs,ys = img.get_size()
        self.size = xs,ys
        tx = power2(xs)
        ty = power2(ys)
        s = pygame.Surface((xs,ys), SRCALPHA, 32)
        s.fill((0,0,0,0))
        s.blit(img.convert_alpha(), (0,0))
        img = pygame.transform.scale(s.convert_alpha(), (tx, ty))
        self.texsize = tx,ty

        s = pygame.Surface((tx,ty), SRCALPHA, 32)
        s.fill((0,0,0,0))
        s.blit(img.convert_alpha(), (0,0))
        size = xs,ys
        bytes = pygame.image.tostring(s.convert_alpha(), "RGBA")
        self._tex = _Texture()
        texid = self._tex.texid
        glBindTexture(GL_TEXTURE_2D, self._tex.texid)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, tx, ty, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes)
        bytes = pygame.image.tostring(img.convert_alpha(), "RGBA")
        #glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, xs, ys, GL_RGBA, GL_UNSIGNED_BYTE, bytes)
        ## TODO: refactor the differences in glTexParameter with Bitmap class
        ## so that there isn't so much duplicated code.
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        minfilter = GL_LINEAR
        magfilter = GL_LINEAR
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, magfilter)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minfilter)
        self.unallocate()

    def _execute(self):        
        tx,ty = self.size
        tx = float(self.rect.width) / tx
        ty = float(self.rect.height) / ty
        x,y = self.rect.topleft
        xx,yy = self.rect.bottomright
        #glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._tex.texid)
        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex2f(x,y)
        glTexCoord2f(tx,0); glVertex2f(xx,y)
        glTexCoord2f(tx,ty); glVertex2f(xx,yy)
        glTexCoord2f(0,ty); glVertex2f(x,yy)
        glEnd()
        #glDisable(GL_TEXTURE_2D)
        
