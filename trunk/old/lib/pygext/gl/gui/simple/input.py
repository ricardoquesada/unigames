
from pygame.locals import *
from pygext.gl.director.entities import TextEntity

__all__ = [
    'TextInputEntity',
    ]

class TextInputEntity(TextEntity):
    def __init__(self, font, scale=None, cursor=None, maxlen=None):
        self.cursor = cursor
        self.maxlen = maxlen
        TextEntity.__init__(self, font, "", scale=scale)
    
    def handle_keydown(self, ev):
        if ev.key in (K_BACKSPACE, K_DELETE):
            self.set_text(self.text[:-1])
        elif not ev.unicode or ord(ev.unicode) < 32:
            return
        elif not self.maxlen or len(self.text) < self.maxlen:
            self.set_text(self.text + ev.unicode)

    def init_text(self, scale=None):
        TextEntity.init_text(self, scale)
        self.update_cursor()

    def update_cursor(self):
        if self.cursor is not None:
            self.cursor.bottom = self.bottom - self.font.font.get_ascent()
            self.cursor.left = self.right
