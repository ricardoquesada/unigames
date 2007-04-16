# -*- coding: iso-8859-1 -*-
import pygame
from pygame.locals import *
from engine import Game, Scene
from menu import Menu
from euclid import *
DEBUG = 0

class MainMenu(Scene):
    def init(self):
        self.menu = Menu(
                 font = pygame.font.Font("data/You Are Loved.ttf",40),
                 font_selected = pygame.font.Font("data/You Are Loved.ttf",60),
                 opts = ( ("Long Jump",self.long_jump),
                        ("High Jump", self.high_jump),
                        ("High Scores", self.high_scores),
                        ("Credits", self.credits),
                        ("Quit", self.end ) ),
                 margin = -38,
                 normal_color = (200,200,200),
                 normal_border_color = (128,128,128),
                 selected_color = (255,255,255),
                 selected_border_color = (50,255,50),
                 rectangle = Point2(640/2,180)
                 )
        
    def render(self):
        self.game.screen.blit(self.background, (0,0))
        self.menu.blit(self.game.screen)

    def long_jump( self ):
        print "Long Jump selected"

    def high_jump( self ):
        print "High Jump selected"

    def high_scores( self ):
        print "high Scores"

    def credits( self ):
        print "credits"

    def update_event(self, evt):
        self.menu.update_event(evt)

    def update( self, dt ):
        pass
