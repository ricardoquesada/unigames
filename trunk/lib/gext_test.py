from pygext.gl.all import *
import pygame

class NiceTextMenu( SimpleTextMenu ):
    def create_selector(self, index, item):
        e = TextEntity(self.font, item.text, scale=self.text_scale-0.01)
        e.center = item.center
        e.color = (20,20,20)
        self.selector_behind = False
        return e

class HelloWorld(Scene):
    def init(self):
        self.font = GLFont( pygame.font.Font("data/You Are Loved.ttf",42) )
        self.circusfont = GLFont( pygame.font.Font("data/KonQa_Black.ttf",80) )
        
        ## All graphical entities are displayed on layers,
        ## so we need to create at least one.
        self.new_layer("unigames",1)
        self.new_layer("menu",2)
        
        text = TextEntity(self.circusfont, "UNIGAMES", scale=1)
        text.centerx = 640/2 
        text.centery = 90
        text.color = (250,250,250)
        text.place("unigames")

        self.menu = NiceTextMenu(items=["New Game", "View Scores","Options","Credits"], font=self.font, scale=1)
        self.menu.centerx = 640/2
        self.menu.centery = 250
        self.menu.place("menu")
        self.menu.select_callback = self.menu_select
        self.menu.escape_callback = director.quit

    def menu_select(self):
        print self.menu.selected

    def escape_select(self):
        director.quit()
    
    ## We'll add a simple keydown event handler to the scene
    ## so that pressing any key will quit the program.        
    def handle_keydown(self, event):
        self.menu.handle_keydown(event)


def main():
    ## Initialize pygext.gl using resolution 800 x 600
    screen.init((640,480))

    ## Start the program
    director.run(HelloWorld)
