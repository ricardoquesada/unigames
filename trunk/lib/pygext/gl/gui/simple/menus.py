
from pygext.gl.director.entities import Entity, EntityNode, TextEntity
from pygext.gl.director.node import Node
from pygext.gl.vector.primitives import rect
from pygext.gl.shapes import draw_shape

from pygame.locals import *

__all__ = [
    'SimpleBaseMenu',
    'SimpleTextMenu',
    ]

class SimpleBaseMenu(EntityNode):

    items = []

##    def __new__(self, *arg, **kw):
##        return object.__new__(self)

    def __init__(self, *arg, **kw):
        EntityNode.__init__(self)
        self.item_ents = []

        self.selector = None
        self.selector_behind = False
        self.selected = 0

        self.select_callback = None
        self.escape_callback = None

        self.menu_init(*arg, **kw)

        self.init_items()
        self.selector = self.create_selector(0, self.item_ents[0])

    def menu_init(self):
        pass ## override in subclass

    def create_item(self, index, item):
        pass ## override in subclass

    def create_selector(self, index, item):
        pass ## override in subclass

    def init_items(self):
        self.item_ents = []
        rect = Rect(0,0,0,0)
        for i, item in enumerate(self.items):
            e = self.create_item(i, item)
            self.item_ents.append(e)
            r = e.get_bounding_rect()
            rect.union_ip(r)
        self.rect = rect

    def get_bounding_rect(self):
        return self.rect.move(self.x, self.y)

    def enter(self):
        if self.selector and self.selector_behind:
            self.selector.traverse()
        for e in self.item_ents:
            e.traverse()
        if self.selector and not self.selector_behind:
            self.selector.traverse()

    def update_selector(self):
        new = self.create_selector(self.selected, self.item_ents[self.selected])
        if new is not None:
            self.selector = new

    def handle_keydown(self, ev):
        if ev.key == K_UP:
            self.selected = (self.selected - 1) % len(self.items)
            self.update_selector()
        elif ev.key == K_DOWN:
            self.selected = (self.selected + 1) % len(self.items)
            self.update_selector()
        elif ev.key in (K_SPACE, K_RETURN):
            if self.select_callback:
                self.select_callback()
        elif ev.key == K_ESCAPE:
            if self.escape_callback:
                self.escape_callback()


class SimpleTextMenu(SimpleBaseMenu):
    def menu_init(self, items, font, scale=1, itemcolor=(255,255,255,255), selectcolor=(0,100,0,255)):
        self.items = items
        self.font = font
        self.itemcolor = itemcolor
        self.selectcolor = selectcolor
        self.selector_behind = True
        self.text_scale = scale

    def create_item(self, index, item):
        e = TextEntity(self.font, item, scale=self.text_scale)
        e.color = self.itemcolor
        e.centerx = 0
        if index == 0:
            e.top = 0
        else:
            prev = self.item_ents[index-1]
            e.top = prev.bottom
        return e

    def create_selector(self, index, item):
        r = item.get_bounding_rect()
        e = Entity(rect(r.width*1.2,r.height).fillcolor(*self.selectcolor))
        e.center = item.center
        return e
