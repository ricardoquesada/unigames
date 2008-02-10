#
# director
# 
#


from pyglet.gl import *
from pyglet import window
from pyglet import clock
from pyglet import media

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
        print '*********** FUCK ************'
        super( Director, self ).__init__( *args, **kw )

        # just for the sake of information
        self.instance = "Instance at %d" % self.__hash__()

    def init( self, *args, **kw ):
        self.window = window.Window( *args, **kw )

    def get_window( self ):
        return self.window

    def push_handlers( self, h ):    
        self.window.push_handlers( h )

    def pop_handlers( self ):
        self.window.pop_handlers()


    def run( self, scenes ):
        """ director main loop """

        fps_display = clock.ClockDisplay()

        if isinstance( scenes, Scene ):
            scenes = ( scenes )
        for s in scenes:
            s.enter()

        while not self.window.has_exit:
            dt = clock.tick()

            self.window.dispatch_events()
            media.dispatch_events()

            for s in scenes:
                s.dispatch_events()

            self.window.clear()

            # Draws
            for s in scenes:
                s.draw()

            fps_display.draw()      # FPS

            self.window.flip()

        for s in scenes:
            s.leave()


#    def on_resize( self, width, height):
#        if height==0:
#            height=1
#        glViewport(0, 0, width, height)
#        glMatrixMode(GL_PROJECTION)
#        glLoadIdentity()
#        gluPerspective(45, 1.0*width/height, 0.1, 100.0)
#        glMatrixMode(GL_MODELVIEW)
#        glLoadIdentity()



director = Director()
