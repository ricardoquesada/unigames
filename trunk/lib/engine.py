# $Id$
#
# this code belongs to "Typos Pocus":  http://www.pyweek.org/e/PyAr2/
#

import sys
import pygame
from pygame.locals import *
DEBUG = 0

class Game:
    def __init__(self, x_size, y_size, framerate=30, title=None, icon=None):
        pygame.mixer.pre_init(44100, -16, False)
        pygame.init()
        pygame.mixer.init()
        self.screen_size = x_size, y_size
        self.x_size = x_size
        self.y_size = y_size
        if icon:
            icon = pygame.image.load(icon)
            icon.set_colorkey((255,0,255))
            pygame.display.set_icon( icon ) 
        self.screen = pygame.display.set_mode((x_size, y_size))
        if title:
            pygame.display.set_caption( title ) 
        pygame.mixer.set_reserved(3)
        self.framerate = framerate   
        self.clock = pygame.time.Clock()
        self.quit = False
        
    def change_scene(self, new_scene):
        self.scene = new_scene

    def main_loop(self):
        while not self.quit:
            self._update_event()
            dt = self.clock.tick(self.framerate)
            self.scene.update(dt)
            self.scene.render()
            pygame.display.flip()

    def _update_event(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                self.quit = True
            elif e.type == KEYDOWN and e.key == K_q:
                self.quit = True
            elif e.type == KEYDOWN and e.key == K_f:
                self.fullscreen()
            else:
                self.scene.update_event(e)

    def fullscreen(self):
        pygame.display.toggle_fullscreen()
   
        
class SceneExit(Exception):
    pass
    
class Scene:
    bg_color = (0,0,0)
    
    @property 
    def background(self):
        if self._background is None:
            self._background = pygame.Surface(self.game.screen.get_size()).convert()
            self._background.fill(self.bg_color)
        return self._background
        
    def __init__(self, game, *args, **kwargs):
        self.game = game
        self._background = None
        self.subscenes = []
        self.init(*args, **kwargs)
        
    def init(self):
        pass
        
    def end(self, value=None):
        self.return_value = value
        self.game.quit = True
        
    def event(self, evt):
        pass
        
    def loop(self):
        pass
        
    def update(self,dt):
        pass
        
    def paint(self):
        self.update()
     
