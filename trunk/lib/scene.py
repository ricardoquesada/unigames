#
#
# Scene class for pyglet
# based on Scene class from pygext
#
#

from pyglet import window

__all__ = [ 'Scene' ]

class Scene(object):
    
    def __init__(self, *args, **kwargs):
        super(Scene, self).__init__(*args, **kwargs)

        self.layers = {}
        self.offset = (0,0)
        self.zoom = 1.0

        self.event_handler = {}


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


class Layer(object):
    def __init__(self):
        self.objects = []
        self.camera = True
        self.visible = True

    def draw(self):
        if self.visible:
            for i in self.objects:
                visible = True
                if hasattr(i,'visible'):
                    visible = i.visible
                if visible:
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
