"""Composite shape
"""

from OpenGL.GL import glPushMatrix, glPopMatrix, glTranslatef
from pygext.gl.shapes.base import GLShape, draw_shape

__all__ = [
    'Composite',
    ]

class Composite(GLShape):
    """Composite shape
    
    The Composite object is used when you want to compose
    a shape from several different shapes, but still be
    able to animate the sub-parts independently.
    """
    def init(self):
        self.parts = []
        self.part_dict = {}

    def compile(self):
        for part in self.parts:
            part.shape.compile()

    def _draw(self):
        self.execute()

    def copy(self):
        obj = GLShape.copy(self)
        obj.parts = []
        obj.part_dict = {}
        for part in self.parts:
            pc = part.copy()
            obj.parts.append(pc)
            obj.part_dict[pc.name] = pc
        return obj

    def get_stencil_poly(self):
        p = None
        for part in self.parts:
            p2 = part.get_stencil_poly()
            if p2 is not None:
                p2.shift(part.x,part.y)
            if p is None:
                p = p2
            else:
                p = p + p2
        return p

##    def make_composite_stencil(self, outline=False):
##        c = Composite()
##        for attr in self.TRANSFORM_ATTRS:
##            setattr(c, attr, getattr(self, attr))
##        for p in self.parts:
##            part = p.copy()
##            part.shape = p.shape.make_stencil(outline)
##            c.parts.append(part)
##            c.part_dict[part.name] = part
##        return c

    def add(self, name, shape, x, y, **kw):
        part = CompositePart(name, shape, x,y, **kw)
        old_part = None
        if name in self.part_dict:
            old_part = self.part_dict.pop(name)
            self.parts.remove(old_part)
        self.parts.append(part)
        self.part_dict[name] = part
        return old_part

    def varcolor(self, r,g,b,a=255):
        for p in self.parts:
            if hasattr(p.shape, "varcolor"):
                p.shape.varcolor(r,g,b,a)

    def mirror(self, target):
        for p in self.parts:
            tpart = target.part_dict.get(p.name)
            if tpart is None:
                continue
            p.mirror(tpart)

    def remove(self, name):
        old = self.part_dict.pop(name)
        self.parts.remove(old)
        return old

    def __getitem__(self, name):
        return self.part_dict[name]

    def _execute(self):
        for part in self.parts:
##            if _global_stencil is not None:
##                glPushMatrix()
##                glTranslatef(part.x,part.y,0)
##                part.shape.execute()
##                glPopMatrix()
##            else:
                draw_shape(part.shape, part.x, part.y)


class CompositePart(object):
    def __init__(self, name, shape, x, y):
        self.shape = shape
        self.name = name
        self.x = x
        self.y = y

    def copy(self):
        part = object.__new__(CompositePart)
        part.__dict__.update(self.__dict__)
        return part

    def mirror(self, target):
        target.x = self.x
        target.y = self.y
