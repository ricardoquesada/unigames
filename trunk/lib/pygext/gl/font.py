"""OpenGL text utilities

This module contains helper utilities for rendering text under
pygext.gl
"""

import pickle
from os.path import join, splitext, isabs
import sys

from OpenGL.GL import *
import pygame
from pygame.locals import *

from pygext.gl.shapes import Bitmap
from pygext.gl.shapes.base import GLShape
from pygext.color import _conv_color


try:
    from Polygon import Polygon
except ImportError:
    pass

__all__ = [
    'GLFont',
    'GLBitmapFont',
    ]

class GLFont(object):
    """OpenGL wrapper for Pygame fonts
    
    If you have a lot of text in your application, this class will help
    you conserve texture memory by pre-generating all visible characters
    in a font and reusing the same textures in each GLText shape.
    """
    
    def __init__(self, font, color=(255,255,255), antialias=True, spacing=0):
        """Create a new GLFont wrapper around a Pygame Font.

        font       - a pygame font object to be converted into an opengl font
	           OR a (fontname, fontsize) tuple
        color      - color of the rendered font (default white)
        antialias  - antialias flag (default True)
	
	Creating a font by its name will first try to load the font from current
	working directory and if that fails, it looks for the font in system fonts.
	
	NOTE: The color parameter should be considered deprecated at this point.
	It's better to leave the font color white, and change the color of individual
	TextEntities instead.
        """
        if isinstance(font, tuple):
            fontname, size = font
            try:
                f = pygame.font.Font(fontname, size)
            except IOError:
                f = pygame.font.SysFont(fontname, size)
            font = f
        self.font = font
        self.color = color
        self.antialias = antialias
        self.spacing = spacing
        self.chardict = {}
        self._generate_surface()
        self.linesize = font.get_linesize()
        self.padding = (0,0,0,0)

    def render(self, text, color=None):
        """Generate a text entity using the font.

        text  - string containing the text
        color - optional color argument (only works if no color was defined for the GLFont object)
	@return GLText shape rendered using the font
        """
        return GLText(self, text, color)


    def _generate_surface(self, chr_range=range(32,128)):
        """
        Internal helper function, that creates a Bitmap entity from each
        separate letter of the font.

        XXX TODO: the letters should be packed more intelligently instead of
        creating a separate texture from each character.
        """
        for c in map(chr, chr_range):
            bmp = self.font.render(c+" ", self.antialias, self.color)
            w,h = self.font.size(c)
            self.chardict[c] = Bitmap(bmp.subsurface(0,0,w+self.spacing,h), hotspot=(0,1))

class BitmapFontData(object):
    def __init__(self):
        self.char_rects = {}
        self.linesize = 0

class GLBitmapFont(GLFont):
    """Bitmap Font

    GLBitmapFont allows you to export a png image file from a font including
    the pixel coordinates for each letter. This png can then be modified in a
    graphics program and loaded back as a GLFont.
    """
    def __init__(self, filename, pngfile=None):
        """Open a previously created bitmap font"""
        if pngfile is None:
            pngfile = splitext(filename)[0]+".png"
##        if not isabs(filename):
##            filename = join(sys.path[0], filename)
##        if not isabs(pngfile):
##            pngfile = join(sys.path[0], pngfile)
        f = open(filename, "rb")
        data = f.read()
        f.close()
        data = pickle.loads(data)
        f.close()
        self.chardict = {}
        s = pygame.image.load(open(pngfile,'rb'))
        for k,v in data.char_rects.iteritems():
            self.chardict[k] = Bitmap(s.subsurface(*v), hotspot=(0,1))
        self.linesize = data.linesize
        self.padding = data.padding

    def create(cls, font, basename, chars=None, padleft=0, padright=0, padtop=0, padbottom=0, antialias=True):
        """Create a bitmap font template

        font - a pygame Font object or a (name,size) tuple
        chars - a string of characters that will be rendered (defaults to characters with ascii code 32-128)
        padleft, padright, padtop, padbottom - add padding to the characters if you intend to add borders/shadows
        """
        if isinstance(font, tuple):
            fontname, size = font
            try:
                f = pygame.font.Font(fontname, size)
            except IOError:
                f = pygame.font.SysFont(fontname, size)
            font = f
        import Image
        if chars is None:
            chars = map(chr, range(32,128))
        datfile = basename+".pxf"
        pngfile = basename+".png"
        surfs = []
        maxheight = 0
        width = 0
        for c in chars:
            surf = font.render(c, antialias, (255,255,255,255))
            w,h = surf.get_size()
            maxheight = max(maxheight, h)
            width += w + padright + padleft
            surfs.append(surf)
        height = maxheight + padtop + padbottom
        surf = pygame.Surface((width,height),SRCALPHA,32)
        surf.fill((0,0,0,0))
        x = 0
        rects = {}
        for c,s in zip(chars,surfs):
            w,h = s.get_size()
            w += padleft + padright
            h += padtop + padbottom
            surf.blit(s, (x+padleft,padtop))
            rects[c] = (x,0,w,h)
            x += w
        dat = pygame.image.tostring(surf,"RGBA")
        img = Image.fromstring("RGBA", surf.get_size(), dat)
        img.save(pngfile, optimize=True)
        dat = BitmapFontData()
        dat.char_rects = rects
        dat.linesize = font.get_linesize() + padtop + padbottom
        dat.padding = (padleft,padright,padtop,padbottom)
        f = open(datfile, "wb")
        pickle.dump(dat, f, 2)
        f.close()
    create = classmethod(create)
        
        

class GLText(GLShape):
    """
    Shape object that represents text.
    
    GLText objects should not usually be created directly,
    but instead via the GLFont.render method.
    
    For short, throwaway texts, you can also contruct a GLText
    object directly from a pygame Font object by calling:
    
    GLFont(font, "Foobar", color=(255,0,0))
    """

    def init(self, glfont, text, color=None):
	"""intializer that is called by GLShape, do not use directly"""
        if type(glfont) is pygame.font.Font:
            from pygext.gl.shapes.bitmap import Bitmap
            s = glfont.render(text, True, color or (255,255,255))
            self.__class__ = Bitmap ## XXX: is this too hoaxy?
            self.init(s)
            return
        self.glfont = glfont
        self.text = text
        self.rect = None
        self.color = color

    def _execute(self):
        glPushMatrix()
        color = self.color
        if color is not None:
            oldcol = glGetFloatv(GL_CURRENT_COLOR)
            glColor4f(*_conv_color(*color))

        xpos = 0
        ypos = 0
        xmax = 0
        height = self.glfont.linesize
        padleft,padright,padtop,padbottom = self.glfont.padding
        glTranslatef(-padleft, height-padtop,0)
        for c in self.text:
            if c == '\n':
                xmax = max(xpos, xmax)
                ypos += height
                glTranslatef(-xpos, height, 0)
                xpos = 0
            bmp = self.glfont.chardict.get(c, None)
            if bmp is None:
                continue
            bmp._execute()
            x,y = bmp.size
            x -= padleft + padright
            glTranslatef(x,0,0)
            xpos += x
        glPopMatrix()
        if color is not None:
            glColor4f(*oldcol)            
        xmax = max(xpos, xmax, 1)
        self.rect = Rect(0,0, xmax, ypos+height)

    def get_stencil_poly(self):
        r = self.rect
        p = Polygon( [ (0,0), (r.right, 0), (r.right, r.bottom), (0, r.bottom) ] )
        return self.trans.transform_polygon(p)

    def get_stencil_rect(self):
        return self.trans.transform_rect(self.rect)
