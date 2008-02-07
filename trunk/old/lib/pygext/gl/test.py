"""base class for internal test scripts: obsolete"""

import pygame
from pygame.locals import *
import pygext.gl as gl

class Test(object):
    def __init__(self):
        gl.screen.init((640,480), (800,600))
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([KEYDOWN])
        self.clock = pygame.time.Clock()
        self.init()

    def mainloop(self):
        while not pygame.event.poll():
            self.render()
            gl.screen.flip()
            gl.screen.clear()
            self.clock.tick(50)
