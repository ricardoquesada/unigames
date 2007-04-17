
__all__ = [
    "Control",
    ]

from pygame import Rect
from OpenGL.GL import *
from pygext.gl.gui.parent import Parent

ATTRS = [
    "x","y",
    "width","height",
    "left","top","right","bottom",
    "center","centerx","centery",
    "topleft", "bottomleft", "topright", "bottomright",
    ]

class Control(Parent):
    """Base class for GUI controls"""

    def __init__(self, parent=None, rect=Rect(0,0,0,0), **kw):
        self.children = []
        self.rect = Rect(rect)
        self.parent = parent
        if parent is not None:
            parent._attach(self)
        self.init(**kw)
        self._list_id = glGenLists(1)
        self._uptodate = False

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name != "_uptodate":
            self._uptodate = False

    def copy(self): # deep copy for gui elements
        obj = object.__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj.children = []
        obj.rect = Rect(self.rect)
        obj._list_id = glGenLists(1)
        for c in self.children:
            obj.children.append(c.copy())
        self.parent._attach(obj)
        obj._uptodate = False
        return obj

    def refresh(self):
        self._uptodate = False

    def init(self):
        pass

    def delete(self):
        self.parent._detach(self)
        self.parent = None
        for c in self.children:
            c.delete()
        if self._list_id is not None:
            glDeleteLists(self._list_id, 1)
            self._list_id = None
        self.__dict__.clear()

    def traverse(self):
        if not self._uptodate:
            glNewList(self._list_id, GL_COMPILE_AND_EXECUTE)
            self.execute()
            glEndList()
            self._uptodate = True
        else:
            glCallList(self._list_id)
        if self.children:
            glPushMatrix()
            glTranslatef(self.rect.left, self.rect.top, 0)
            for c in self.children:
                c.traverse()
            glPopMatrix()

    def execute(self):
        pass

    def pick(self, x, y):
        if not self.rect.collidepoint(x,y):
            return None        
        x -= self.rect.left
        y -= self.rect.top
        for c in self.children:
            result = c.pick(x,y)
            if result is not None:
                return result
        return self

    def set(self, **kw):
        for k,v in kw.iteritems():
            setattr(self, k, v)
        return self

    def __del__(self):
        if hasattr(self,"_list_id") and self._list_id is not None:
            glDeleteLists(self._list_id, 1)

    ############
    ## Events ##
    ############

    def on_enter(self): pass
    def on_exit(self): pass
    def on_click(self): pass
    def on_right_click(self): pass
    def on_rect_change(self): pass
    

def delegate():
    for a in ATTRS:
        s = \
"""def _getter(self):
    return self.rect.*
def _setter(self, value):
    self.rect.* = value
    self.on_rect_change()""".replace("*", a)
        exec s
        setattr(Control, a, property(_getter, _setter))
        
delegate()
