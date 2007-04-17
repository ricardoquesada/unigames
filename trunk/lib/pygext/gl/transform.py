"""Shape transformations

Internal implementation for shape transformations. The
functionality in this module should not be used directly,
but instead bia the GLShape API. The module implements the
following transformations:
    
GLShape.translate(x,y)
GLShape.scale(x,y)
GLShape.rotate(degrees)
GLShape.transform(matrix)
GLShape.skewx(x)
GLShape.skewy(y)
"""

import pygame
from pygame.locals import Rect
from OpenGL.GL import *
from OpenGL.GLU import gluProject

try:
    from Polygon import Polygon
except ImportError:
    pass

__all__ = [
    "Transformation",
    ]

def _skewy(x):
    glMultMatrixf([1,x,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])

def _skewx(x):
    glMultMatrixf([1,0,0,0, x,1,0,0, 0,0,1,0, 0,0,0,1])

TRANSDICT = {
    'translate': glTranslatef,
    'scale': glScalef,
    'rotate': glRotatef,
    'transform': glMultMatrixf,
    'skewx': _skewx,
    'skewy': _skewy,
    }

_identity = (1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
_viewport = (0,0,2,8/3.0)

def project_polygon(p, model=None):
    p2 = Polygon()
    if model is None:
        model = glGetDoublev(GL_MODELVIEW_MATRIX)
    for i,c in enumerate(p):
        hole = p.isHole(i)
        points = []
        for x,y in c:
            px,py,pz = gluProject(x,y,0,model, _identity, _viewport)
            points.append((px,py))
        p2.addContour(points, hole)
    return p2

class least(object):
    def __lt__(self, other):
        return True
    def __gt__(self, other):
        return False
least = least()

class most(object):
    def __lt__(self, other):
        return False
    def __gt__(self, other):
        return True
most = most()

def project_rect(r, model=None):
    if model is None:
        model = glGetDoublev(GL_MODELVIEW_MATRIX)

    maxx,maxy = least,least
    minx,miny = most,most
    for x,y in [(r.left,r.top), (r.right,r.top), (r.right,r.bottom), (r.left,r.bottom)]:
        px,py,pz = gluProject(x,y,0,model,_identity,_viewport)
        maxx = max(maxx, px)
        maxy = max(maxy, py)
        minx = min(minx, px)
        miny = min(miny, py)
    return Rect(minx,miny,maxx-minx,maxy-miny)

def project_point(x, y):
    model = glGetDoublev(GL_MODELVIEW_MATRIX)
    px,py,pz = gluProject(x,y,0,model,_identity, _viewport)
    return px,py


class Transformation(object):

    __slots__ = ()

    def transform_polygon(self, poly):
        glPushMatrix()
        glLoadIdentity()
        self.execute()
        p = project_polygon(poly)
        glPopMatrix()
        return p

    def transform_rect(self, rect):
        glPushMatrix()
        glLoadIdentity()
        self.execute()
        r = project_rect(rect)
        glPopMatrix()
        return r
        

    def reset(self):
        pass ## implement in subclass

    def copy(self):
        pass ## implement in subclass

    def execute(self):
        pass ## implement in subclass

class AccumulatedTransform(Transformation):
    __slots__ = ("_transforms",)
    
    def __init__(self):
        Transformation.__init__(self)
        self._transforms = []

    def translate(self, dx, dy):
        self._transforms.append(('translate',(dx,dy,0)))

    def scale(self, sx, sy=None):
        if sy is None:
            sy = sx
        self._transforms.append(('scale', (sx,sy,1)))

    def rotate(self, angle):
        self._transforms.append(('rotate', (angle,0,0,1)))

    def skewx(self, ratio):
        self._transforms.append(('skewx', (ratio,)))

    def skewy(self, ratio):
        self._transforms.append(('skewy', (ratio,)))

    def reset(self):
        del self._transforms[:]

    def copy(self):
        obj = object.__new__(AccumulatedTransform)
        obj._transforms = self._transforms[:]
        return obj

    def execute(self):
        trans = self._transforms
        indices = range(len(trans))
        indices.reverse()
        for i in indices:
            funcname, args = trans[i]
            func = TRANSDICT[funcname]
            func(*args)

SLOTS = ("x", "y", "angle", "scale", "_matrix")

class IdentityTransform(Transformation):
    x = 0
    y = 0
    angle = 0
    scale = 1

    def transform_polygon(self, poly):
        return poly

    def __setattr__(self, key, value):
        object.__setattr__(self, "__class__", SimpleTransform)
        self.reset()
        setattr(self, key, value)
    
class SimpleTransform(Transformation):
    """Deprecated class. Was used with Node objects in an earlier implementation.
    """
   
    def __init__(self):
        Transformation.__init__(self)
        self.reset()      

    def reset(self):
        osa = object.__setattr__
        osa(self, "x", 0)
        osa(self, "y", 0)
        osa(self, "angle", 0)
        osa(self, "scale", 1)
        osa(self, "_matrix", None)

    def copy(self):
        obj = object.__new__(SimpleTransformation)
        osa = object.__setattr__
        osa(obj, "x", self.x)
        osa(obj, "y", self.y)
        osa(obj, "angle", self.angle)
        osa(obj, "scale", self.scale)
        osa(obj, "_matrix", None)

    def _compile(self):
        glPushMatrix()
        glLoadIdentity()
        self._execute()
        self._matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        glPopMatrix()

    def execute(self):
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0,0,1)
        scale = self.scale
        if type(scale) is not tuple:
            scale = (scale,scale)
        glScalef(scale[0],scale[1],0)

        
