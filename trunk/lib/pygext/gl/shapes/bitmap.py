"""Raster image base classes
"""

from OpenGL.GL import *
import pygame
from pygame.locals import SRCALPHA, Rect
import math
import os, sys
from os.path import exists

from pygext.gl.shapes.base import GLShape

try:
    from Polygon import Polygon
except ImportError:
    pass

try:
    import pyg
except ImportError:
    pyg = None

try:
    from psyco.classes import *
except:
    pass

__all__ = [
    'Bitmap',
    ]

def power2(x):
    """power2(x) -> nearest power of two
    
    Calculate the nearest power of two that is equal
    or greater than x.
    """
    p = math.log(x) / math.log(2)
    return 2**int(math.ceil(p))

MAX_TEXTURE_SIZE = 512

class _Texture(object):
    def __init__(self):
        self.texid = glGenTextures(1)
        #print "init tex", self.texid

    def __del__(self):
        if hasattr(self, "texid") and self.texid is not None and glDeleteTextures is not None:
            glDeleteTextures([self.texid])
            #print "del tex",self.texid

class Bitmap(GLShape):
    """A shape representing a raster image
    
    This class is used to wrap Pygame surfaces to OpenGL
    textures.
    """
    use_filtering = True
    default_hotspot = (0.5,0.5)
    border = False
    
    def init(self, img, hotspot=None, border=None):
	"""Bitmap(surface, hotspot=(0.5,0.5))
	
	Initialize a new Bitmap object.
	
	surface - Pygame surface to wrap
	hotspot - The hotspot is used as a fixed point for transformations.
		  Valid values range from (0,0) to (1,1) (top left to bottom right).
		  The center of the image is (0.5, 0.5)
	"""
	if hotspot is None:
            hotspot = self.default_hotspot
        if border is not None:
            self.border = border
        img = self._load_surf(img)
        self._tex = None
        self.hotspot = hotspot
	self._subimages = None
        self._setimage(img)

    def _load_surf(img):
        if isinstance(img, basestring):
            if not exists(img) and pyg is not None:
                img = pygame.image.load(pyg.openfile(img))
            else:
##                if not os.path.isabs(img):
##                    img = os.path.join(sys.path[0], img)
                img = pygame.image.load(open(img,'rb'))
        return img
    _load_surf = staticmethod(_load_surf)

    def copy(self):
        bmp = object.__new__(Bitmap)
        bmp.__dict__.update(self.__dict__)
        bmp._listid = None
        return bmp

    def set_hotspot(self, rx, ry):
        self.hotspot = (rx,ry)
        self.unallocate()
        return self

    def get_stencil_poly(self):
        xs,ys = self.size
        hx,hy = self.hotspot
        hx *= -xs
        hy *= -ys
        p = Polygon([(hx,hy), (hx+xs,hy), (hx+xs,hy+ys), (hx,hy+ys)])
        return self.trans.transform_polygon(p)

    def get_stencil_rect(self):
        xs,ys = self.size
        hx,hy = self.hotspot
        hx *= -xs
        hy *= -ys
        r = Rect(hx,hy,xs,ys)
        return self.trans.transform_rect(r)

    def _make_subimages(self, img, size=MAX_TEXTURE_SIZE):
	xs,ys = img.get_size()
	xsegments = xs // size
	ysegments = ys // size
	xleftover = xs % size
	yleftover = ys % size

	rows = []
	y = 0
	for y in range(ysegments):
	    row = []
	    rows.append(row)
	    for x in range(xsegments):
		subimg = img.subsurface((x*size,y*size,size,size))
		row.append(Bitmap(subimg, hotspot=(0,0)))
	    if xleftover:
		subimg = img.subsurface((xsegments*size,y*size, xleftover, size))
		row.append(Bitmap(subimg, hotspot=(0,0)))
	if yleftover:
	    row = []
	    rows.append(row)
	    x = 0
	    for x in range(xsegments):
		subimg = img.subsurface((x*size,ysegments*size,size,yleftover))
		row.append(Bitmap(subimg, hotspot=(0,0)))
	    if xleftover:
		subimg = img.subsurface((size*xsegments,size*ysegments, xleftover, yleftover))
		row.append(Bitmap(subimg, hotspot=(0,0)))
	self._subimages = rows
	self._subimagesize = size
    
    def _setimage(self, img):

        xs,ys = img.get_size()
	self.size = xs,ys
	if self.border:
            xs += 2
            ys += 2
	
	if xs > MAX_TEXTURE_SIZE or ys > MAX_TEXTURE_SIZE:
	    self._make_subimages(img)
	    self.unallocate()
	    return
	
        tx = power2(xs)
        ty = power2(ys)
        self.texsize = tx,ty

        s = pygame.Surface((tx,ty), SRCALPHA, 32)
        s.fill((0,0,0,0))
        s.blit(img.convert_alpha(), (0,0))
        size = xs,ys
        bytes = pygame.image.tostring(s.convert_alpha(), "RGBA")
        self._tex = _Texture()
        glBindTexture(GL_TEXTURE_2D, self._tex.texid)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, tx, ty, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes)        
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)            
        if self.use_filtering:
            magfilter = GL_LINEAR
            minfilter = GL_LINEAR
        else:
            minfilter = GL_NEAREST
            magfilter = GL_NEAREST
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, magfilter)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minfilter)
        self.unallocate()

    def _execute(self):
        xs,ys = self.size
        hx,hy = self.hotspot
        hx *= -(xs)
        hy *= -(ys)
	if self._subimages:
	    if hx or hy:
		glTranslatef(hx,hy,0)
	    for i,row in enumerate(self._subimages):
		glPushMatrix()
		if i > 0:
		    glTranslatef(0,i*self._subimagesize,0)
		for img in row:
		    img._execute()
		    glTranslatef(self._subimagesize,0,0)
		glPopMatrix()
	    return
		
        #glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self._tex.texid)
        glBegin(GL_QUADS)
        if self.border:
            tx,ty = self.texsize
            cx = 1/float(tx)
            cy = 1/float(ty)
            tx = (xs-1)/float(tx)
            ty = (ys-1)/float(ty)
            glTexCoord2f(cx,cy); glVertex2f(hx,hy)
            glTexCoord2f(tx,cy); glVertex2f(hx+xs,hy)
            glTexCoord2f(tx,ty); glVertex2f(hx+xs,hy+ys)
            glTexCoord2f(cx,ty); glVertex2f(hx,hy+ys)
        else:
            tx,ty = self.texsize
            tx = xs/float(tx)
            ty = ys/float(ty)
            glTexCoord2f(0,0); glVertex2f(hx,hy)
            glTexCoord2f(tx,0); glVertex2f(hx+xs,hy)
            glTexCoord2f(tx,ty); glVertex2f(hx+xs,hy+ys)
            glTexCoord2f(0,ty); glVertex2f(hx,hy+ys)
        glEnd()
        #glDisable(GL_TEXTURE_2D)

    def _particle_execute(self):
        xs,ys = self.size
        hx,hy = self.hotspot
        hx *= -(xs)
        hy *= -(ys)
		
        tx,ty = self.texsize
        tx = xs/float(tx)
        ty = ys/float(ty)

        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex2f(hx,hy)
        glTexCoord2f(tx,0); glVertex2f(hx+xs,hy)
        glTexCoord2f(tx,ty); glVertex2f(hx+xs,hy+ys)
        glTexCoord2f(0,ty); glVertex2f(hx,hy+ys)
        glEnd()

