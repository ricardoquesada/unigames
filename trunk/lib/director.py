#
# director
# A Director() ( like in movies ), is an object is in charge of everything
#


from pyglet import window
from pyglet import clock
from pyglet import media

# Singleton
class _Singleton( window.Window ):
    def __init__(self, *args, **kw ):
        super( _Singleton, self ).__init__( *args, **kw )

        # just for the sake of information
        self.instance = "Instance at %d" % self.__hash__()

    def run( self, scene ):

        fps_display = clock.ClockDisplay()
   
        scene.enter()

        while not self.has_exit:
            dt = clock.tick()

            self.dispatch_events()
            media.dispatch_events()

            scene.dispatch_events()

            self.clear()

            # Draws
            scene.draw()
            fps_display.draw()      # FPS

            self.flip()

        scene.leave()

_singleton = _Singleton()

def Director( *args, **kw ):
    return _singleton
