from pygext.gl.all import *
import os,pygame
from pygame.locals import *

def imgcolorkey(image, colorkey):
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_image(filename, colorkey = None):
    filename = os.path.join('data', filename)
    image = pygame.image.load(filename).convert()
    return imgcolorkey(image, colorkey)

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = load_image(filename)
    def imgat(self, rect, colorkey = None):
        rect = Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        return imgcolorkey(image, colorkey)

class GameTest(Scene):
    def enter(self):
        self.new_layer("images")
        self.new_layer("background",-10)

        # Create three identical entities, which use a different hotspot
        # (0,0) = top left corner
        # (0.5, 0.5) = center of the image
        # (1,1) = bottom right corner
        self.image1 = Entity("data/unicycle.png", hotspot=(0.5,0.5))
        self.image2 = Entity("data/unicycle.png", hotspot=(0.5,0.5))
        self.image3 = Entity("data/unicycle.png", hotspot=(0.5,0.5))

        # Set the entities side by side. Note that if you would
        # set the x and y attributes of the entities, they wouldn't
        # be neatly lined up, because their hotspot is different.
        self.image1.set(left=100, top=200).place("images")
        self.image2.set(left=300, top=200).place("images")
        self.image3.set(left=500, top=200).place("images")

        #
        spritesheet = SpriteSheet('blocks1.bmp')
        surf = spritesheet.imgat((444, 104, 32, 32))

        for i in range(1,30):
            self.image4 = Entity( surf )
            self.image4.set(left=300, top=300).place("background")


        self.set_state("pirulowaitkey")

    def state_pirulowaitkey_handle_keydown(self, event):
        # press any key to rotate the Entities around their hotspot
        self.set_state("rotating")
        self.image1.do(Rotate(90))
        self.image2.do(Rotate(360))
        self.image3.do( Fork( Rotate(-180), Scale(2,3, mode=PingPongMode) ) )
        self.image3.do( MoveTo( 0,0, 4, mode=PingPongMode) )

    def state_rotating_handle_keydown(self, event):
        director.quit()
