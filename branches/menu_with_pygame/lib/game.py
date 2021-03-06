# $Id$
# UniGames - Unicycle Games
#

import pygame
from pygame.locals import *
from engine import Game, Scene
import time, random
from mainmenu import MainMenu
DEBUG = 0


class JoustSprite(pygame.sprite.Sprite):
    def __init__(self, initial_position=(0,0) ):
        pygame.sprite.Sprite.__init__(self)
        surf = pygame.image.load("data/joust.png").convert_alpha()

        self.images = []
        for i in xrange(0,360):
            self.images.append( pygame.transform.rotate( surf, i ) )

        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position

        self.image_index = 0

    def update( self, *args ):
        self.image_index = (self.image_index + 1) % 360
        print self.image_index
        self.image = self.images[self.image_index]


class UnicycleSprite(pygame.sprite.Sprite):
    def __init__(self, initial_position=(0,0) ):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("data/unicycle_joust.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position

class JoustGame(Scene):
    
    def init(self):
#        self._background = pygame.image.load("data/background_joust.png").convert()
        self._background = pygame.image.load("data/TerrainMain.jpg").convert()
        self.unicycle_joust = UnicycleSprite( (0,200))
        self.joust = JoustSprite( (0,200))

    def update_event(self, evt):
        if evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                self.end()
            elif evt.key == K_RIGHT:
                self.unicycle_joust.rect.x += 5
            elif evt.key == K_LEFT:
                self.unicycle_joust.rect.x -= 5
            elif evt.key == K_UP:
                self.unicycle_joust.rect.y -= 5
            elif evt.key == K_DOWN:
                self.unicycle_joust.rect.y += 5

    def loop(self):
        pass

    def render( self ):
        self.game.screen.blit(self.background, (0,0))
        self.unicycle_joust.update()
        self.game.screen.blit(self.unicycle_joust.image, self.unicycle_joust.rect)
        self.game.screen.blit(self.joust.image, self.unicycle_joust.rect)

    def update(self, dt):
        pass

def main():
    g = Game(640, 480, framerate = 30, title = "Unicycle Games")
    g.change_scene( MainMenu(g) )
    g.main_loop()

if __name__ == "__main__":
    main()
