#
# A playground file to test the framework
#
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import sys

from pyglet import image
from pyglet.gl import *
from pyglet import media

from menu import Menu, MenuItem, ToggleMenuItem
from scene import Scene, MultiplexScene 
from director import *

class MainMenu(Menu):
    def __init__( self ):
        super( MainMenu, self ).__init__("GROSSINI'S SISTERS" )
        self.items.append( MenuItem('New Game', self.on_new_game ) )
        self.items.append( MenuItem('Options', self.on_options ) )
        self.items.append( MenuItem('Scores', self.on_scores ) )
        self.items.append( MenuItem('Quit', self.on_quit ) )
        self.reset()


    # Callbacks
    def on_new_game( self ):
        print "ON NEW GAME"
        director.set_scene( StartGame() )

    def on_scores( self ):
        print "ON SCORES"

    def on_options( self ):
        self.switch_to( 1 )

    def on_quit( self ):
        sys.exit()

class OptionMenu(Menu):
    def __init__( self ):
        super( OptionMenu, self ).__init__("GROSSINI'S SISTERS" )
        self.items.append( MenuItem('Fullscreen', self.on_fullscreen) )
        self.items.append( ToggleMenuItem('Sound', True, self.on_sound) )
        self.items.append( ToggleMenuItem('Show FPS', True, self.on_show_fps) )
        self.items.append( MenuItem('OK', self.on_quit) )
        self.reset()

        self.fullscreen = False

    # Callbacks
    def on_fullscreen( self ):
        self.fullscreen = not self.fullscreen
        director.get_window().set_fullscreen( self.fullscreen )

    def on_sound( self, value ):
        print "on_sound: %s" % value

    def on_quit( self ):
        self.switch_to( 0 )

    def on_show_fps( self, value ):
        director.enable_FPS( value )

class AnimatedSprite( Scene ):
    def __init__( self ):
        super( AnimatedSprite, self).__init__( self )
        self.sprite_sister1 = image.load('data/grossinis_sister1.png')
        self.sprite_sister2 = image.load('data/grossinis_sister2.png')

        self.background_sound= media.load('data/the great gianna sisters.mp3', streaming=True)
        self.player = media.Player()
        self.player.queue( self.background_sound )

        self.heading = 0

    def enter( self ):
        self.player.play()

    def exit( self ):
        self.player.pause()

    def draw( self ):
#        print "AnimatedSprite: draw()"
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(120, 280, 0)
        glRotatef(self.heading, 0, 0, 1)
        self.sprite_sister1.blit( -20, -50 )

        glLoadIdentity()
        glTranslatef(420, 280, 0)
        glRotatef(-self.heading, 0, 0, 1)
        self.sprite_sister2.blit( -20, -50 )
        glPopMatrix()

    def dispatch_events( self ):
        self.player.dispatch_events()

    def tick( self, dt ):
        self.heading += 1.5

class OpenGLTest( Scene ):
    def __init__( self ):
        super( OpenGLTest, self).__init__( self )
        self.rquad = 0.0

    def enter( self ):
        pass

    def exit( self ):
        pass

    def draw( self ):

        glPushMatrix()
        glLoadIdentity()

        glTranslatef(320,100,0)

        glRotatef(self.rquad, 0.0, 0.0, 1.0)

        glPushAttrib( GL_CURRENT_BIT )
        glBegin(GL_QUADS)
        glColor3f(0.5, 0.5, 1.0)
        glVertex3f(-20.0, 20.0, 0)
        glColor3f(0.5, 1.0, 0.5)
        glVertex3f(20.0, 20.0, 0)
        glColor3f(1.0, 0.5, 0.5)
        glVertex3f(20.0, -20.0, 0)
        glColor3f(0.5, 0.5, 0.5)
        glVertex3f(-20.0, -20.0, 0)
        glEnd()

        glPopAttrib()

        glPopMatrix()

    def tick( self, dt ):
        self.rquad += dt * 40


class StartGame( OpenGLTest ):
    def tick( self, dt ):
        self.rquad -= dt * 100 



def run():

    from pyglet import font

    font.add_directory('data')

    director.init( caption = "Grossini's Sisters", resizable = True )
    director.run( ( OpenGLTest(),
                    AnimatedSprite(),
                    MultiplexScene(
                        ( MainMenu(), OptionMenu() )
                        ) ) )



if __name__ == "__main__":
    run()
