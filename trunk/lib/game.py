__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import sys

from pyglet import image
from pyglet.gl import *
from pyglet import media

from menu import Menu, MenuItem, ToggleMenuItem
from scene import Scene, XorScene 
from director import *

class StartGame( Scene ):
    def __init__( self ):
        super( StartGame, self ).__init__( self )
        
    def enter( self ):
        print "StartGame: enter()"

    def quit( self ):
        print "StartGame: quit()"

    def draw( self ):
        print "StartGame: draw()"


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
        print 'xxxxxxxxxxxxx 1'
        sys.exit()

class OptionMenu(Menu):
    def __init__( self ):
        super( OptionMenu, self ).__init__("GROSSINI'S SISTERS" )
        self.items.append( MenuItem('Fullscreen', self.on_fullscreen) )
        self.items.append( ToggleMenuItem('Sound', True, self.on_sound) )
        self.items.append( ToggleMenuItem('Show FPS', True, self.on_show_fps) )
        self.items.append( MenuItem('OK', self.on_quit) )
        self.reset()

    # Callbacks
    def on_fullscreen( self ):
        pass

    def on_sound( self, value ):
        print "on_sound: %s" % value

    def on_quit( self ):
        print 'xxxxxxxxxxxxx 0'
        self.switch_to( 0 )

    def on_show_fps( self, value ):
        director.enable_FPS( value )

class AnimatedSprite( Scene ):
    def __init__( self ):
        super( AnimatedSprite, self).__init__( self )
        self.sprite_sister1 = image.load('data/grossinis_sister1.png')
        self.sprite_sister2 = image.load('data/grossinis_sister2.png')
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.background_sound= media.load('data/the great gianna sisters.mp3', streaming=True)

        self.heading = 0

    def enter( self ):
        print "AnimatedSprite: enter()"
        self.background_sound.play()

    def exit( self ):
        print "AnimatedSprite: exit()"
        del self.background_sound

    def draw( self ):
#        print "AnimatedSprite: draw()"
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(120, 280, 0)
        glRotatef(self.heading, 0, 0, 1)
        self.sprite_sister1.blit( -20, -50 )

        glLoadIdentity()
        self.sprite_sister2.blit( 420, 280 )
        glPopMatrix()


    def tick( self, dt ):
        self.heading += 1.5

class OpenGLTest( Scene ):
    def __init__( self ):
        super( OpenGLTest, self).__init__( self )
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        self.rquad = 0.0

    def enter( self ):
        print "OpenGLText: enter()"
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    def exit( self ):
        print "OpenGLText: exit()"

    def draw( self ):

        glPushMatrix()
        glLoadIdentity()

        glTranslatef(100,100,0)

        glRotatef(self.rquad, 0.0, 0.0, 1.0)

#        glColor3f(0.5, 0.5, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(-20.0, 20.0, 0)
        glVertex3f(20.0, 20.0, 0)
        glVertex3f(20.0, -20.0, 0)
        glVertex3f(-20.0, -20.0, 0)
        glEnd()
        glPopMatrix()

    def tick( self, dt ):
        self.rquad += dt * 40


def run():

    from pyglet import font

    font.add_directory('data')

    director.init( caption = "Grossini's Sisters" )
    director.run( ( OpenGLTest(),
                    AnimatedSprite(),
                    XorScene(
                        ( MainMenu(), OptionMenu() )
                        ) ) )



if __name__ == "__main__":
    run()
