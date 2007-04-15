#
# UniGames
#

import pygame
from pygame.locals import *

class Game:
    def __init__(self, fps = 20, screensize = Rect(0,0,640,480) ):
        self.__fps =  fps
        self.__screensize = screensize

        pygame.init()
        screen = pygame.display.set_mode( self.__screensize, 0)

        self.initIntro()

    def run(self):
        while true:
            self.showIntro()
            game = self.selectGame()
            game.run()

    def initIntro( self ):
        pass
    def showIntro( self ):
        pass
