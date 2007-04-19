from pygext.gl.all import *

class NiceTextMenu( SimpleBaseMenu ):
    def menu_init(self, items, font, scale=1, itemcolor=(255,255,255,255), selectcolor=(0,100,0,255), top_margin=5):
        self.items = items
        self.font = font
        self.itemcolor = itemcolor
        self.selectcolor = selectcolor
        self.selector_behind = True
        self.text_scale = scale
        self.last_item_selected = -1
        self.top_margin = top_margin    # distances between options

    def create_item(self, index, item):
        e = TextEntity(self.font, item, scale=self.text_scale)
        e.color = self.itemcolor
        e.centerx = 0
        if index == 0:
            e.top = 0
        else:
            prev = self.item_ents[index-1]
            e.top = prev.bottom - self.top_margin
        return e

    def create_selector(self, index, item):
        if self.last_item_selected >= 0:
            self.item_ents[self.last_item_selected].end_actions()
            self.item_ents[self.last_item_selected].scale = 1
        e = TextEntity(self.font, item.text, scale=self.text_scale)
        e.center = item.center
        e.color = (255,64,64)
        e.do( Scale(1.26,0.2) )
        self.item_ents[index].do( Scale(1.25,0.2) )
        self.last_item_selected = index
        return e
