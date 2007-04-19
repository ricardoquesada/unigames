from pygext.gl.all import *

class GameTest(Scene):
    def enter(self):
        self.new_layer("images")

        # Create three identical entities, which use a different hotspot
        # (0,0) = top left corner
        # (0.5, 0.5) = center of the image
        # (1,1) = bottom right corner
        self.image1 = Entity("data/unicycle.png", hotspot=(0,0))
        self.image2 = Entity("data/unicycle.png", hotspot=(0.5,0.5))
        self.image3 = Entity("data/unicycle.png", hotspot=(1,1))

        # Set the entities side by side. Note that if you would
        # set the x and y attributes of the entities, they wouldn't
        # be neatly lined up, because their hotspot is different.
        self.image1.set(left=100, top=200).place("images")
        self.image2.set(left=300, top=200).place("images")
        self.image3.set(left=500, top=200).place("images")

        self.set_state("waitkey")

    def state_waitkey_handle_keydown(self, event):
        # press any key to rotate the Entities around their hotspot
        self.set_state("rotating")
        self.image1.do(Rotate(90))
        self.image2.do(Rotate(90))
        self.image3.do(Rotate(90))

    def state_rotating_handle_keydown(self, event):
        director.quit()
