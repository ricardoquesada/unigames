#
#
# Director class for pyglet
#
# Ideas borrowed from:
#    pygext: http://opioid-interactive.com/~shang/projects/pygext/
# 
#

from pyglet.gl import *
from pyglet import window
from pyglet import clock
from pyglet import media

import gc

from scene import Scene

__all__ = [ 'director', 'Director' ]

#
# Director: sort of singleton
#
class Director( object ):
    """Scene director

    The director is the element that controls the main loop
    and calls event handlers, updates actions, etc. You should
    not create instances of this class manually, as the default
    instance is automatically initialized and other components depend
    on that instance.
    """

    def __init__(self, *args, **kw ):
        super( Director, self ).__init__( *args, **kw )

        # just for the sake of information
        self.instance = "Instance at %d" % self.__hash__()

        self.scene = None
        self.next_scene = None
        self.show_FPS = True


    def init( self, *args, **kw ):
        """ init( *args, **kw ) -> None

        initialize pyglets main Window with *args and **kw as parameters.
        this method shall be called before run()
        """

        # create main pyglet window
        self.__window = window.Window( *args, **kw )

        # save resolution and aspect for resize / fullscreen
        self.__window.on_resize = self.on_resize
        self.__window_original_res_x = self.__window.width
        self.__window_original_res_y = self.__window.height
        self.__window_aspect =  self.__window.width / float( self.__window.height )
        self.__offset_x = 0
        self.__offset_y = 0

        self._enable_alpha_blending()

    def get_window_size( self ):
        """get_window_size() -> (x,y)

        Returns the original window size, and not the resolution.
        In Fullscreen mode the resolution is different from the Window mode
        but the size is emulated.
        """
        return ( self.__window_original_res_x, self.__window_original_res_y)
        
    #
    # enable alpha blending
    # images with "alpha" channel will be shown according to that value
    #
    def _enable_alpha_blending( self ):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    #
    # return the pyglet Window
    #
    def get_window( self ):
        """get_window( bool ) -> Window

        returns the pyglet main Window.
        """
        return self.__window

    #
    # show FPS in left bottom corner
    #
    def enable_FPS( self, value ):
        """enable_FPS( bool ) -> None

        Show FPS at the bottom left or not.
        """
        self.show_FPS = value

    #
    # director main loop
    # scene is 1 scene or a list of scenes
    # These scenes will be run all together.
    # If you want to change the scene, just call set_scene()
    #
    def run( self, scene ):
        """run( scenes ) -> None

        Executes the list of scenes (or the scene) at the same time.
        Scenes that are first in the list, will be executed (draw) first.
        """

        fps_display = clock.ClockDisplay()

        if isinstance( scene, Scene ):
            self.scene = ( scene, )
        else:
            self.scene = scene

        # scenes initialization before being shown
        for s in self.scene:
            s.enter()

        while not self.__window.has_exit:

            if self.next_scene is not None:
                s,a,kw = self.next_scene
                self._set_scene(s, *a, **kw)

            dt = clock.tick()

            # dispatch pyglet events
            self.__window.dispatch_events()
            media.dispatch_events()

            # custom scenes: dispatch events, and ticks them
            for s in self.scene:
                s.tick( dt )
                s.dispatch_events()

            # clear pyglets main window
            self.__window.clear()

            # Draws all the elements again
            for s in self.scene:
                s.draw()

            # show the FPS
            if self.show_FPS:
                fps_display.draw()

            # show all the changes
            self.__window.flip()


        # scenes clenaup
        for s in self.scene:
            s.exit()

    #
    # to change to a new scene or list of scenes
    #
    def set_scene( self, scene, *args, **kw ):
        self.next_scene = (scene, args, kw)

    def _set_scene(self, scene, *arg, **kw):
        """Change to a new scene.
        """

        self.next_scene = None
        gc.collect()
        if gc.garbage:
            print "WARNING: your application produced %i items of garbage" % len(gc.garbage)
            print gc.garbage[:25]

        if self.scene is not None:
            for s in self.scene:
                s.exit()

            for s in self.scene:
                for name,layer in s.layers.items():
                    layer[1].clear()
                    s.del_layer(name)

        gc.collect()

        if isinstance( scene, Scene ):
            self.scene = ( scene, )
        else:
            self.scene = scene

        for s in self.scene:
            s.enter(*arg, **kw)


    #
    # get virtual coordinates
    #
    def get_virtual_coordinates( self, x, y ):
        """get_virtual_coordinates( x, y ) -> (int, int)

        Converts real coordinates to virtual (or screen) coordinates.
        If you are working with a window "real" coordinates and "virtual"
        coordinates are the same, but if you are in fullscreen mode, then
        the "real" and "virtual" coordinates might be different since fullscreen mode 
        doesn't change the resolution of the screen. Instead it uses all the screen,
        so the "real" coordinates are the coordinates of all the screen.
        """

        x_diff = self.__window_original_res_x / float( self.__window.width - self.__offset_x * 2 )
        y_diff = self.__window_original_res_y / float( self.__window.height - self.__offset_y * 2 )

        adjust_x = (self.__window.width * x_diff - self.__window_original_res_x ) / 2
        adjust_y = (self.__window.height * y_diff - self.__window_original_res_y ) / 2

        return ( int( x_diff * x) - adjust_x,   int( y_diff * y ) - adjust_y )

    #
    # window resize handler
    #
    def on_resize( self, width, height):
        width_aspect = width
        height_aspect = int( width / self.__window_aspect)

        if height_aspect > height:
            width_aspect = int( height * self.__window_aspect )
            height_aspect = height

        self.__offset_x = (width - width_aspect) / 2
        self.__offset_y =  (height - height_aspect) / 2

        glViewport(self.__offset_x, self.__offset_y, width_aspect, height_aspect )
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.__window_original_res_x, 0, self.__window_original_res_y, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)


director = Director()
