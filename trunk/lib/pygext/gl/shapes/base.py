"""The base GLShape class and basic operations
"""

from OpenGL.GL import *
from pygame.locals import Rect

from pygext.gl.transform import AccumulatedTransform as Transformation
from pygext.color import _conv_color

try:
    from psyco.classes import *
except ImportError:
    pass


try:
    from Polygon import Polygon
except ImportError:
    Polygon = None

__all__ = [
    'GLShape',
    'draw_shape',
    'combine',
    'FuncObject',
    ]

def draw_shape(shape, x, y, rot=0, scale=1.0, color=None,
               glPushMatrix=glPushMatrix,
               glTranslatef=glTranslatef,
               glRotatef=glRotatef,
               glScalef=glScalef,
               glColor4b=glColor4b,
               glColor4f=glColor4f,
               glPopMatrix=glPopMatrix):
    """
    draw_shape(shape, x, y, rotation=0, scale=1.0) -> None

    Draw a pygext.gl shape to the display. Note: you must call
    pygext.gl.flip_screen() for the changes to become visible.
    """
    glPushMatrix()
    glTranslatef(x,y,0)
    if rot != 0:
        glRotatef(rot, 0,0,1)
    if scale != 1.0 and scale is not None:
        if type(scale) is not tuple:
            scale = (scale,scale)
        glScalef(scale[0],scale[1],1)
    if color is not None:
        oldcol = glGetFloatv(GL_CURRENT_COLOR)
        glColor4f(*_conv_color(*color))
        shape._draw()
        glColor4f(*oldcol)
    else:
        shape._draw()
    glPopMatrix()


class GLShape(object):
    """Abstract pygext.gl graphics object
    
    Base shape object that knows how to cache its drawing
    routines into an opengl display list and supports
    transformations such as scale and rotate.
    """

    
    def __init__(self, *arg, **kw):
        self._listid = None
        self.trans = Transformation()
        self._alpha = None
        self.init(*arg, **kw)

	
    def init(self, *arg, **kw):
        """
        Two-phase initialization
        Override this in subclasses
        """
        pass

    def compile(self):
        """shape.compile() -> None

        Compile the shape into a display list for quicker output.
        If you manipulate the shape in anyway (e.g. rotate/scale),
        you need to call compile again.
        """
        self.unallocate()
        i = glGenLists(1)
        glNewList(i, GL_COMPILE)
        self.execute()
        glEndList()
        if Polygon:
            poly = self.get_stencil_poly()
            self.bounding_poly = poly
            if poly:
                xmin,xmax,ymin,ymax = poly.boundingBox()
                self.bounding_rect = Rect(xmin,ymin,xmax-xmin,ymax-ymin)
            else:
                self.bounding_rect = self.get_stencil_rect()
        else:
            self.bounding_rect = self.get_stencil_rect()
        self._listid = i
        return self

    def copy(self):
        """shape.copy() -> new shape object

        Create a fresh copy of the shape that can be manipulated
        wihtout altering the original.
        """
        obj = object.__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj._listid = None
        obj.trans = self.trans.copy()
        return obj

    def unallocate(self):
        """shape.unallocate() -> None

        Free the opengl display list used by this shape.
        """
        if self._listid is None:
            return
        glDeleteLists(self._listid, 1)
        self._listid = None

    def __getattr__(self, name):
        f = getattr(self.trans, name)
        def wrapper(*arg, **kw):
            f(*arg, **kw)
            return self
        return wrapper


    def alpha(self, a):
        """shape.alpha(alpha) -> shape

        Sets an overal alpha transparency for the whole shape.
        Note: only effective after a new compile.

        Valid alpha values are 0-255
        """
        self._alpha = a
        return self

    def get_stencil_poly(self):
        return None

    def get_stencil_rect(self):
        return Rect(0,0,0,0)

    def execute(self):
        """shape.execute() -> None
        
        Execute the opengl commands to draw this shape along
        with all transformations.
        """
        if self._alpha is not None:
            _global_alpha.append(self._alpha * _global_alpha[-1])
        glPushMatrix()

        self.trans.execute()

        ## call subclass
        self._execute()

        glPopMatrix()
        if self._alpha is not None:
            _global_alpha.pop()

    def _draw(self):
        """shape._draw() -> None

        Just like shape.execute(), but uses a cached display list
        if one is available. Otherwise creates the list.
        """
        if glGetIntegerv(GL_LIST_INDEX):
            return self.execute()
        if self._listid is None:
            self.compile()
        glCallList(self._listid)

    def _execute(self):
        "override this in a subclass"

    def __del__(self):
        if glDeleteLists is None:
            return
        self.unallocate()

def combine(*shapes):
    """combine(shape1, shape2, shape3, ...) -> GLShape

    Creates a new shape object by combining several existing shape objects.
    After combining, the individual shapes can no longer be accessed or modified.

    If you want an object whose sub-objects you can manipulate later, use the
    Composite object.
    """
##    def execute_all():
##        for s in shapes:
##            s.execute()
##    return FuncObject(execute_all)
    return Merged(shapes)

class Merged(GLShape):
    """Shape composed of separate sub-shapes
    
    See the combine function for more details.
    """
    
    def init(self, shapelist):
        self.shapes = shapelist

    def _execute(self):
        for s in self.shapes:
            s.execute()

    def get_stencil_poly(self):
        p = None
        for s in self.shapes:
            p2 = s.get_stencil_poly()
            if p2 is not None:
                if p is None:
                    p = p2
                else:
                    p = p + p2
        return p


class FuncObject(GLShape):
    """
    A shape object which is drawn in an external function.
    """
    
    def init(self, _func, *args, **kw):
        self._func = _func
        self._args = args
        self._kw = kw

    def _execute(self):
        self._func(*self._args, **self._kw)
