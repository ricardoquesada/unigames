#
#
# Director class for pyglet
# riq - 2008
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
    and calls event handlers, updates actions etc. You should
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
        # create main window
        self.__window = window.Window( *args, **kw )

        # save resolution and aspect for resize / fullscreen
        self.__window.on_resize = self.on_resize
        self.__window_original_res_x = self.__window.width
        self.__window_original_res_y = self.__window.height
        self.__window_aspect =  self.__window.width / float( self.__window.height )

        self.enable_alpha_blending()

    #
    # enable alpha blending
    # images with "alpha" channel will be shown according to that value
    #
    def enable_alpha_blending( self ):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    #
    # return the pyglet Window
    #
    def get_window( self ):
        return self.__window

    #
    # show FPS in left bottom corner
    #
    def enable_FPS( self, value ):
        self.show_FPS = value

    #
    # director main loop
    # scene is 1 scene or a list of scenes
    #
    def run( self, scene ):
        """ director main loop """

        fps_display = clock.ClockDisplay()

        if isinstance( scene, Scene ):
            self.scene = ( scene, )
        else:
            self.scene = scene

        # scenes will be shown
        for s in self.scene:
            s.enter()

        while not self.__window.has_exit:

            if self.next_scene is not None:
                s,a,kw = self.next_scene
                self._set_scene(s, *a, **kw)

            dt = clock.tick()

            self.__window.dispatch_events()
            media.dispatch_events()

            for s in self.scene:
                s.tick( dt )
                s.dispatch_events()

            self.__window.clear()

            # Draws
            for s in self.scene:
                s.draw()

            if self.show_FPS:
                fps_display.draw()      # FPS

            self.__window.flip()

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
    # window resize handler
    #
    def on_resize( self, width, height):
        width_aspect = width
        height_aspect = int( width / self.__window_aspect)

        if height_aspect > height:
            width_aspect = int( height * self.__window_aspect )
            height_aspect = height

        center_x = (width - width_aspect) / 2
        center_y =  (height - height_aspect) / 2

        glViewport(center_x, center_y, width_aspect, height_aspect )
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.__window_original_res_x, 0, self.__window_original_res_y, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)


director = Director()
