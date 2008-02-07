"""Utilities for handling mouse in OpenGL mode
"""


class GLMouse(object):
    def __init__(self):
        self.pointer = None
        self.x = 0
        self.y = 0

    def get_pos(self):
        return self.x,self.y

    def _init_default_cursors(self):
        from pygext.gl.director.entities import Entity
        import pygext.gl as gl
        self.default_pointer = Entity(gl.__path__[0]+"/cursor1.png", hotspot=(0,0))        

glmouse = GLMouse()
