
__all__ = [
    "Root",
    ]

from pygame.locals import *

from pygext.gl.director.globals import director
from pygext.gl.gui.parent import Parent
from pygext.gl.mouse import glmouse

class Root(Parent):

    fast_draw = False
    
    def __init__(self):
        Parent.__init__(self)
        scene = director.scene

        self.hover = None

    def clear(self):
        for c in self.children:
            c.delete()

    def tick(self):
        mx,my = glmouse.get_pos()
        for c in self.children:
            ctrl = c.pick(mx,my)
            if ctrl is not None:
                self._set_hover(ctrl)
                break
        else:
            self._set_hover(None)

    def handle_events(self, events):
        for ev in events:
            if ev.type == MOUSEBUTTONUP:
                if self.hover is not None:
                    if ev.button == 1:
                        self.hover.on_click()
                    elif ev.button == 3:
                        self.hover.on_right_click()

    def _set_hover(self, ctrl):
        if ctrl is not None and self.hover is not ctrl:
            ctrl.on_enter()
        if self.hover is not None:
            self.hover.on_exit()
        self.hover = ctrl
            
