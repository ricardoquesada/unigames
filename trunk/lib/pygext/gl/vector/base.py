##
## pyVectorGFX - base classes
##
## author: Sami Hangaslammi
## email:  shang@iki.fi
##

from pygext.color import _conv_color, Gradient
from pygext.gl.shapes import GLShape
from pygext.math.vecalg import *

_global_alpha = [1.0]
_global_stencil = None

from OpenGL.GL import *
from OpenGL.GLU import gluProject
import pygame
from pygame.locals import *
import Numeric as N
import math

try:
    from Polygon import Polygon
except ImportError:
    pass

class InheritColor(object): pass

class Primitive(GLShape):
    """
    New implementation for primitive objects
    """
    def init(self, polygon):
        self._polygon = polygon
        self._fillcolor = None
        self._linecolor = None
        self._linewidth = 1
        self._linestipple = None
        self._lineaa = False

    def mirror_style(self, source):
        self._fillcolor = source._fillcolor
        self._linecolor = source._linecolor
        self._linewidth = source._linewidth
        self._linestipple = source._linestipple
        self._lineaa = source._lineaa

    def fillcolor(self, r, g=None, b=None, a=255):
        if g is None:
            assert b is None
            if type(r) is tuple:
                self._fillcolor = _conv_color(*r)
            else:
                self._fillcolor = r
        else:
            self._fillcolor = _conv_color(r,g,b,a)
        return self
    color = fillcolor

    def linecolor(self, r,g,b,a=255):
        self._linecolor = _conv_color(r,g,b,a)
        return self

    def linestipple(self, scale, pattern):
        self._linestipple = (scale, pattern)
        return self

    def linewidth(self, width):
        self._linewidth = width
        return self

    def lineantialias(self, aa):
        self._lineaa = aa
        return self

    def get_interior(self, delta):
        p = self._polygon
        p2 = Polygon()
        for i,c in enumerate(p):
            points = []
            for ii,pts in enumerate(c):
                previ = (ii-1) % len(c)
                nexti = (ii+1) % len(c)
                A = N.array(pts)
                B = N.array(c[previ])
                C = N.array(c[nexti])
                AB = B-A
                AC = C-A
                D = midnormal(AB,AC)
                if p.isHole(i):
                    D = -D
##                a = angle(-AB, AC)
##                #a = angle(AC) - angle(-AB)
##                if a < 0:
##                    a += 360
##                if a > 180:
##                    D = -D
                    
                x = tuple(D*delta + A)
                # adjust for non-convex points
                if not p.isInside(*x):
                    D = -D
                    x = tuple(D*delta + A)
                
                points.append(x)
            p2.addContour(points, p.isHole(i))
        return Primitive(p2)

    def hollow(self, border=1):
        self._polygon -= self.get_interior(border)._polygon
        return self

    def transformed_polygon(self):
        return self.trans.transform_polygon(self._polygon)

    def projected_polygon(self):
        return self.trans._project_poly(self._polygon)

    get_stencil_poly = transformed_polygon

    def _execute(self):
        glDisable(GL_TEXTURE_2D)
        self._execute_fill()
        self._execute_line()
        glEnable(GL_TEXTURE_2D)

    def _execute_fill(self):
        if self._fillcolor is None:
            return
        if not isinstance(self._fillcolor, Gradient):
            if self._fillcolor is not InheritColor:
                glColor4f(*self._fillcolor)
            grad = None
        else:
            grad = self._fillcolor
            bounds = self._polygon.boundingBox()
        strips = self._polygon.triStrip()
        vx=glVertex2f
        for s in strips:
            glBegin(GL_TRIANGLE_STRIP)
            for x,y in s:
                if grad is not None:
                    glColor4f(*grad.get_color(x,y,bounds))
                vx(x,y)
            glEnd()
        #glColor4f(1,1,1,1)

    def _execute_line(self):
        if self._linecolor is None:
            return
        if self._linecolor is not InheritColor:
            glColor4f(*self._linecolor)
        if self._linestipple is not None:
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(*self._linestipple)
        else:
            glLineStipple(1, 0xffff)
        glLineWidth(self._linewidth)
        if self._lineaa:
            glEnable(GL_LINE_SMOOTH)
        else:
            glDisable(GL_LINE_SMOOTH)
        for contour in self._polygon:
            ## GL_LINE_LOOP doesn't work for non-convex polygons on older cards
##            glBegin(GL_LINE_LOOP)
##            for x,y in contour:
##                glVertex2f(x,y)
##            glEnd()
            glBegin(GL_LINE_STRIP)
            for x,y in contour:
                glVertex2f(x,y)
            glVertex2f(*contour[0])
            glEnd()
        if self._linestipple is not None:
            glDisable(GL_LINE_STIPPLE)
        #glColor4f(1,1,1,1)


        
class glprimitive(object):
    _modifiers = {}
    
    def __init__(self, func):
        self._func = func

    def __call__(self, *arg, **kw):
        return Primitive(self._func(*arg, **kw))

