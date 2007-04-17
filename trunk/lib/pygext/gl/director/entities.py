"""Entities

Entities serve pretty much the same function as Sprites do in Pygame.
Each entity has a shape (see pygext.gl.shapes.base.GLShape) it uses to
draw itself, and entities can have actions (see pygext.gl.director.actions)
performed on them.

Usually, Entities aren't draw on the screen manually. Instead you place them
on layers (see pygext.gl.director.scene), and the Scene renders them
automatically.
"""

from OpenGL.GL import *
import pygame
from pygame.locals import *
import weakref

try:
    Set = set
except NameError:
    from sets import Set

try:
    from psyco.classes import *
except ImportError:
    pass

try:
    from Polygon import Polygon
except ImportError:
    Polygon = None

from pygext.gl.shapes import GLShape, draw_shape, Composite, Bitmap
from pygext.gl.resources import resources
from pygext.gl.director.globals import director
from pygext.gl.transform import Transformation, project_point
from pygext.color import _conv_color

from pygext.gl.director.node import Node

__all__ = [
    'Entity',
    'EntityNode',
    'StaticEntity',
    'TextEntity',
    ]

class EntityNode(Node):
    """Base class for all Entities
    
    A simple entity that uses a single shape to draw itself.
    """
    image = None
    layer = None

##    __slots__ = ("shape", "color", "static_rect")
       
    def __init__(self, shape=None, hotspot=None, **kw):
        Node.__init__(self)
        if shape is None and self.image is not None:
            shape = self.image
        if isinstance(shape, basestring):
            name = shape
            shape = resources.get_bitmap(name, hotspot)
        elif isinstance(shape, pygame.Surface):
            shape = Bitmap(shape)
        if shape is not None and shape._listid is None:
            shape.compile()
        self.shape = shape
        self.color = None
        self.static_rect = None
        if self.layer is not None:
            self.place(self.layer)
        self.init(**kw)

    def _delete(self):
        self.shape = None
        Node._delete(self)

    def init(self):
        pass # override in subclass
    
    def place(self, layername):
	"""place(layername) -> this
	
	Place the entity on a layer in the currently active Scene.
	"""
        director.scene.add(layername, self)
        return self

    def set(self, **kw):
	"""set(**kw) -> this
	
	Set several attribute in one call, for example:
	    
	entity.set(x=10, y=20, angle=90)
	"""
        for k,v in kw.iteritems():
            setattr(self, k, v)
        return self

    if Polygon:
        def get_bounding_rect(self):
            """get_bounding_rect() -> Rect
            
            Calculate the bounding rect for the entity.
            """
            if self.static_rect is not None:
                return self.static_rect.move(self.x, self.y)
            if self.angle or self.scale != 1:
                p = self.transform_polygon(self.shape.bounding_poly)
                xmin,xmax,ymin,ymax = p.boundingBox()
                return Rect(xmin,ymin,xmax-xmin,ymax-ymin)
            else:
                r = self.shape.bounding_rect
                return r.move(self.x, self.y)
    else:
        def get_bounding_rect(self):
            """get_bounding_rect() -> Rect
            
            Calculate the bounding rect for the entity.
            """
            if self.static_rect is not None:
                return self.static_rect.move(self.x, self.y)
            if self.angle or self.scale != 1:
                r = self.transform_rect(self.shape.bounding_rect)
                return r
            else:
                r = self.shape.bounding_rect
                return r.move(self.x, self.y)
        

##    def get_real_bounding_rect(self):
##        """get_real_bounding_rect() -> Rect
##
##        Get the bounding rect of the entity after doing
##        all transformations in the nodepath so far. Used
##        for collision testing.
##        """
##        if self.static_rect is not None:
##            return self.static_rect.move(self.realx, self.realy)
##        if self.angle or self.scale != 1:
##            p = self.transform_polygon(self.shape.bounding_poly)
##            xmin,xmax,ymin,ymax = p.boundingBox()
##            return Rect(xmin,ymin,xmax-xmin,ymax-ymin)
##        else:
##            r = self.shape.bounding_rect
##            return r.move(self.realx, self.realy)


    def set_alpha(self, alpha):
        r,g,b = (self.color or (255,255,255))[:3]
        self.color = (r,g,b,alpha)

    def get_alpha(self):
        return (self.color or (255,255,255,255))[3]


    alpha = property(get_alpha, set_alpha)

    ###########################
    ##  Position Properties  ##
    ###########################

    def _get_width(self):
        b = self.get_bounding_rect()
        return b.width
    width = property(_get_width)
    def _get_height(self):
        b = self.get_bounding_rect()
        return b.height
    height = property(_get_height)

    def _get_center(self):
        b = self.get_bounding_rect()
        return b.center
    def _set_center(self, (x,y)):
        cx,cy = self._get_center()
        self.x += x-cx
        self.y += y-cy
    center = property(_get_center, _set_center)

    def _get_centerx(self):
        b = self.get_bounding_rect()
        return b.centerx
    def _set_centerx(self, x):
        cx = self._get_centerx()
        self.x += x-cx
    centerx = property(_get_centerx, _set_centerx)        

    def _get_centery(self):
        b = self.get_bounding_rect()
        return b.centery
    def _set_centery(self, y):
        cy = self._get_centery()
        self.y += y-cy
    centery = property(_get_centery, _set_centery)

    def _get_right(self):
        b = self.get_bounding_rect()
        return b.right
    def _set_right(self, x):
        b = self.get_bounding_rect()
        self.x += x-b.right
    right = property(_get_right, _set_right)

    def _get_bottom(self):
        b = self.get_bounding_rect()
        return b.bottom
    def _set_bottom(self, y):
        b = self.get_bounding_rect()
        self.y += y-b.bottom
    bottom = property(_get_bottom, _set_bottom)

    def _get_left(self):
        b = self.get_bounding_rect()
        return b.left
    def _set_left(self, x):
        b = self.get_bounding_rect()
        self.x += x-b.left
    left = property(_get_left, _set_left)

    def _get_top(self):
        b = self.get_bounding_rect()
        return b.top
    def _set_top(self, y):
        b = self.get_bounding_rect()
        self.y += y-b.top
    top = property(_get_top, _set_top)

    def enter(self):
        if self.shape:
            color = self.color
            if color is not None:
                r,g,b,a = _conv_color(*color)
                if not a:
                    return
                glColor4f(r,g,b,a)
            else:
                glColor4f(1,1,1,1)
            self.shape._draw()

class Entity(EntityNode):

##    __slots__ = ()
    fast_draw = True
    
    def _attach(self, other, back=False):
        raise TypeError, "Cannot attach entities to Entity. Use EntityNode as a parent instead."

class StaticEntity(EntityNode):
    """Transformations can change, but visual outlook doesn't"""

    def __init__(self, *arg, **kw):
        EntityNode.__init__(self, *arg, **kw)
        self._listid = glGenLists(1)
        self._static_uptodate = False

    def refresh(self):
        self._static_uptodate = False

    def _draw_here(self):
        glRotatef(self.angle, 0,0,1)
        scale = self.scale
        if type(scale) is not tuple:
            scale = (scale,scale)
        glScalef(scale[0],scale[1],0)
        if director.ticker.realtick:
            self.realx, self.realy = project_point(0,0)
	    for n in self._collision_nodes:
		n.realx, n.realy = project_point(n.x, n.y)
	if self._static_uptodate:
            glCallList(self._listid)
        else:
            glNewList(self._listid, GL_COMPILE_AND_EXECUTE)
            filter(Node.traverse, self.bchildren)
            self.enter()
            filter(Node.traverse, self.fchildren)
            self.exit()
            glEndList()
            self._static_uptodate = True
    
    def __del__(self):
        glDeleteLists(self._listid, 1)

class TextEntity(Entity):
    """Mutable text entity
    
    A text label that updates itself when the text is changed.
    """
    def __new__(self, font, *arg, **kw):
        if not hasattr(font, "render"):
            raise TypeError, "GLFont object expected as the fist argument to %s" % self.__name__
        return object.__new__(self)
    
    def __init__(self, font, text="", scale=None):
        Entity.__init__(self)
        self.font = font
        self.text = text
        self.text_scale = scale
        self.init_text(scale)

    def init_text(self, scale=None):
	"""internal helper function"""
        self.shape = self.font.render(self.text)
        if scale is None:
            scale = self.text_scale
        if scale is not None:
            self.shape.scale(scale)
        self.shape.compile()

    def set_text(self, text, scale=None):
	"""set_text(text [,scale]) -> None
	
	Change the contents of the text entity.
	"""
        if text == self.text:
            return
        self.text = text
        self.init_text(scale)

    
