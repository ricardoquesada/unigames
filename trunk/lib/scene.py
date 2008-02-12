# $Id$
#
# Scene class for pyglet
# based on Scene class from pygext and other projects
#
#

from pyglet import window
from pyglet import event

__all__ = [ 'Scene', 'MultiplexScene', 'Layer' ]

class Scene(object):
    
    def __init__(self, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)

        self.layers = {}


    ########################
    ##  Subclass Methods  ##
    ########################

    def enter(self, *arg, **kw):
        """This method is called when the scene is activated. Override in a subclass."""
        pass ## override in subclass

    def exit(self):
        """This method is called when the scene ends. Override in a subclass."""
        pass ## override in subclass

    def tick(self, dt):
        """ This method is called once per cycle. dt is "delta time" from the last tick."""
        pass  ## override in subclass


    def draw(self):
        """ This method is called once per cycle. Subclasses shall draw everything.
        Don't override this method if you want to work with layers
        """
        for d,l in self.layers.itervalues():
            l.draw()


    #####################
    ##  Layer Methods  ##
    #####################

    def new_layer(self, name, depth=None, camera=False):
        """new_layer(name, depth=None) -> Layer
        
        Create a new entity layer to the scene. If depth is omitted,
        the layer will be created on top of all previously created layers.
        """
        layer = Layer()
        layer.enable_camera(camera)
        if depth is None:
            try:
                depth = max(self.layers.itervalues())[0]+1
            except ValueError:
                depth = 0
        self.layers[name] = [depth, layer]
        self._reorder()
        return layer


    def get_layer(self, name):
        """get_layer(name) -> Layer
        
        Get a specific layer using its name.
        """
        return self.layers[name][1]

    def set_depth(self, layername, depth):
        """set_depth(layername, depth) -> None
        
        Set a new depth for the given layer.
        """
        self.layers[layername][0] = depth
        self._reorder()

    def del_layer(self, name):
        """del_layer(layername) -> None
        
        Delete the specified layer.
        """
        del self.layers[name]
        self._reorder()

    def __getitem__(self, layername):
        return self.layers[layername][1]

    def _reorder( self ):
        pass


#
# MultiplexScene
# 
# A Composite scene that only enables one scene at the time
# This is useful, for example, when you have 3 or 4 menus, but you want to
# show one at the time
#
class MultiplexScene( Scene ):
    def __init__( self, scenes ):
        super( MultiplexScene, self ).__init__()

        self.scenes = scenes
        self.enabled_scene = 0

        for s in self.scenes:
            s.switch_to = self.switch_to

    def switch_to( self, scene_number ):
        if scene_number < 0 or scene_number >= len( self.scenes ):
            raise Exception("MultiplexScene: Invalid scene number")

        self.scenes[ self.enabled_scene ].exit()
        self.enabled_scene = scene_number
        self.scenes[ self.enabled_scene ].enter()

    def tick( self, dt):
        self.scenes[ self.enabled_scene ].tick( dt )

    def draw( self ):
        self.scenes[ self.enabled_scene ].draw()

    def enter( self ):
        self.scenes[ self.enabled_scene ].enter()

    def quit( self ):
        self.scenes[ self.enabled_scene ].quit()


class Layer(object):
    def __init__(self):
        self.objects = []
        self.camera = True
        self.visible = True

    def draw(self):
        if self.visible:
            for i in self.objects:
                i.draw()

    def append( self, o ):
        self.objects.append( o )

    def enable_camera(self, flag=True):
        self.camera = flag

    def set_visible( self, flag=True):
        self.visible = flag

    def clear( self ):
        """ sort of clean-up method """
        pass

    def __getitem__(self, index):
        return self.objects[ index ]
