__docformat__ = 'restructuredtext'
__version__ = '$Id$'

from pyglet import image
from pyglet.gl import *
from pyglet import media

from menu import Menu
from scene import Scene
from director import *

class GameMenu(Menu):
    def __init__( self ):
        super( GameMenu, self ).__init__( self, title="GROSSINI'S SISTERS",
                options=( ("New Game", self.on_new_game )
                        , ("Scores", self.on_scores)
                        , ("Options", self.on_options)
                        , ("Quit", self.on_quit) )
                        )

    # Callbacks
    def on_new_game( self ):
        print "ON NEW GAME"

    def on_scores( self ):
        print "ON SCORES"

    def on_options( self ):
        print "ON OPTIONS"

    def on_quit( self ):
        print "ON QUIT"

class AnimatedSprite( Scene ):
    def __init__( self ):
        super( AnimatedSprite, self).__init__( self )
        self.sprite_sister1 = image.load('data/grossinis_sister1.png')
        self.sprite_sister2 = image.load('data/grossinis_sister2.png')
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.background_sound= media.load('data/the great gianna sisters.mp3', streaming=True)

    def enter( self ):
        self.background_sound.play()

    def leave( self ):
        pass

    def draw( self ):
        self.sprite_sister1.blit( 120, 280 )
        self.sprite_sister2.blit( 420, 280 )


def run():
    director.init( caption = "Grossini's Sisters" )
    director.run( ( AnimatedSprite(), GameMenu() ) )


if __name__ == "__main__":
    run()
