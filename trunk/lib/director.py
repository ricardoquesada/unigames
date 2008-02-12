#
#
# director class
# heavily based on pygext director class
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
#        kw['resizable'] = True
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

    def get_window( self ):
        return self.__window

    def push_handlers( self, h ):    
        self.__window.push_handlers( h )

    def pop_handlers( self ):
        self.__window.pop_handlers()

    def enable_FPS( self, value ):
        self.show_FPS = value

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

            self.__window.clear()

            # Draws
            for s in self.scene:
                s.draw()

            if self.show_FPS:
                fps_display.draw()      # FPS

            self.__window.flip()

        for s in self.scene:
            s.exit()


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


#    def on_resize( self, width, height):
#        if height==0:
#            height=1
#        glViewport(0, 0, width, height)
#        glMatrixMode(GL_PROJECTION)
#        glLoadIdentity()
#        gluPerspective(45, 1.0*width/height, 0.1, 100.0)
#        glMatrixMode(GL_MODELVIEW)
#        glLoadIdentity()

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
