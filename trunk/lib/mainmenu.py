from pygext.gl.all import *
import pygame
from menu import *
import level_muni
import game

class UniMainMenu(Scene):
    def init(self):
        self.font = GLFont( pygame.font.Font("data/You Are Loved.ttf",42) )
        self.circusfont = GLFont( pygame.font.Font("data/KonQa_Black.ttf",80) )
        
        self.new_layer("unigames",1)
        self.new_layer("menu",2)
        
        self.text = TextEntity(self.circusfont, "UNIGAMES", scale=1 )
        self.text.center = (640/2, 90)
        self.text.color = (250,250,250)
        self.text.place("unigames")

        self.menu = NiceTextMenu(items=["New Game", "View Scores","Options","Credits"], font=self.font, scale=1)
        self.menu.center = (640/2, 250)
        self.menu.place("menu")
        self.menu.select_callback = self.menu_select
        self.menu.escape_callback = self.escape_select

        self.game = game.Game()


    def menu_select(self):
        if self.menu.selected == 0:
            director.set_scene(level_muni.LevelMuni, game.Game() )

#        elif self.menu.selected == 1:
#            director.set_scene(HighScores)

        elif self.menu.selected == 2:
            director.set_scene(UniOptionMenu)

#        elif self.menu.selected == 3:
#            director.set_scene(Credits)

    def escape_select(self):
        director.quit()
    
    def handle_keydown(self, event):
        self.menu.handle_keydown(event)

class UniOptionMenu(Scene):
    def init(self):
        self.font = GLFont( pygame.font.Font("data/You Are Loved.ttf",42) )
        self.circusfont = GLFont( pygame.font.Font("data/KonQa_Black.ttf",80) )
        
        self.new_layer("unigames",1)
        self.new_layer("menu",2)
        
        self.text = TextEntity(self.circusfont, "UNIGAMES", scale=1 )
        self.text.center = (640/2, 90)
        self.text.color = (250,250,250)
        self.text.place("unigames")

        self.menu = NiceTextMenu(items=["Toggle Fullscreen"], font=self.font, scale=1)
        self.menu.center = (640/2, 250)
        self.menu.place("menu")
        self.menu.select_callback = self.menu_select
        self.menu.escape_callback = self.escape_select


    def menu_select(self):
        if self.menu.selected == 0:
            pygame.display.toggle_fullscreen()

        if self.menu.selected == 1:
            self.escape_select()

    def escape_select(self):
        director.set_scene( UniMainMenu )
    
    def handle_keydown(self, event):
        self.menu.handle_keydown(event)


def main():
    screen.init((640,480),(640,480),fullscreen=False,title="UNIGAMES")
#    director.visible_collision_nodes = True
    director.run(UniMainMenu)
