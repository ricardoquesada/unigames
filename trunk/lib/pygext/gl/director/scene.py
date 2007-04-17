"""Scene handling

Scenes are used to abstract different kinds of event loops in your game.
You could, for example, have a scene for title screen, main game loop and
hiscore screen. Usually, pygext.gl.director.Director control transition
from one scene to another.

Scene rendering consists of layers of entities. Layers are used to control
the z-ordering of the sprites ie. entities as well as grouping the entities
into logical groups (for e.g. collision detection).

A single scene can have several states. Different states can have separate
mainloop logic and separate event handling.
"""


import pygame
from pygame.locals import *
from OpenGL.GL import *

try:
    Set = set
except NameError:
    from sets import Set

try:
    from psyco.classes import *
except:
    pass


from pygext.gl.director.entities import *
from pygext.gl.shapes import GLShape
from pygext.color import _conv_color
from pygext.gl.director.node import Node
from pygext.gl.director.globals import director
from pygext.gl.transform import Transformation, project_point

from pygext.debug import debugmode, print_obj_stats

import re

try:
    from psyco.classes import *
except ImportError:
    pass

__all__ = [
    'Scene',
    ]

EVENTS = [
    QUIT,
    ACTIVEEVENT,
    KEYDOWN,
    KEYUP,
    MOUSEMOTION,
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN,
    JOYAXISMOTION,
    JOYBALLMOTION,
    JOYHATMOTION,
    JOYBUTTONUP,
    JOYBUTTONDOWN,
    VIDEORESIZE,
    VIDEOEXPOSE,
    USEREVENT,
    ]

class Scene(object):
    collengine = None
    
    def __init__(self, *arg, **kw):
        self.layers = {}
        self.depth_cache = []
        self.state = ""
        self.offset = (0,0)
        self.zoom = 1.0
        if self.collengine is not None:
            self.coll = self.collengine()
        else:
            self.coll = None
        self.event_handler = {}
        for event in EVENTS:
            handlers = {}
            funcname = "handle_" + pygame.event.event_name(event).lower()
            if hasattr(self, funcname):
                handlers[""] = getattr(self, funcname)
            for name in dir(self.__class__):
                if name.startswith("state_"):
                    s = name.split("_")
                    statename = s[1]
                    s = "_".join(s[2:])
                    if s == funcname:
                        handlers[statename] = getattr(self, name)
            if handlers:
                self.event_handler[event] = handlers
        for fn in self.__class__.__dict__:
            m = re.match(r"collision_(\w+)_(\w+)$", fn)
            if m:
                group1 = m.group(1)
                group2 = m.group(2)
                self.set_collision_handler(group1, group2, getattr(self, fn))
        self.init(*arg, **kw)


    ########################
    ##  Subclass Methods  ##
    ########################

    def init(self):
	"""This method is called when the scene is created. Override in a subclass."""
        pass ## override in subclass

    def tick(self):
	"""This method is called once per frame. Overide in a subclass
	
	You can also prefix the tick-method with the state name to make
	state-spesific tick functions. E.g.
	
	def state_main_tick(self):
	    pass
	def state_waitkey_tick(self):
	    pass
	...
	"""
        pass ## override in subclass

    def realtick(self):
        pass ## override in subclass

    def enter(self, *arg, **kw):
	"""This method is called when the scene is activated. Override in a subclass."""
        pass ## override in subclass

    def exit(self):
	"""This method is called when the scene ends. Override in a subclass."""
        pass ## override in subclass

    ######################
    ##  State Handling  ##
    ######################

    def set_state(self, new_state):
        self.state = new_state
        director.set_state(new_state)


    ######################
    ##  Event Handling  ##
    ######################

    def handle_events(self, events):
	"""handle_events(events) -> None
	
	Delegates pygame events to specific event handling methods.
	This method is usually called by the Director and should not
	be used directly.
	"""
	if debugmode:
            for e in events:
                if e.type == KEYDOWN:
                    if e.key == K_c:
                        director.visible_collision_nodes ^= True
                    elif e.key == K_s:
                        print_obj_stats()
        for e in events:
            handlers = self.event_handler.get(e.type)
            if handlers:
                func = handlers.get(self.state)
                if not func:
                    func = handlers.get("", lambda e: None)
                func(e)


    def handle_quit(self, event):
	"""Default handler for pygame.QUIT event is to stop the Director"""
        from pygext.gl.director.globals import director
        director.quit()


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

    def new_stabile(self, name, depth=None, camera=False):
        """Create a new stable layer

        On a stable layer, entities retain their original z-order, but
        adding and removing entities is slower. Use when your entities
        need to overlap.
        """
        layer = StabileLayer()
        layer.enable_camera(camera)
	if depth is None:
	    try:
		depth = max(self.layers.itervalues())[0]+1
	    except ValueError:
		depth = 0
        self.layers[name] = [depth, layer]
        self._reorder()
        return layer

    def new_static(self, name, depth=None, camera=False):
	"""new_static(name, depth=None) -> layer
	
	Create a new static layer to the scene. Static layers offer
	much better performance for a high number of entities, but
	once placed on this layer, no change in the entities is
	reflected on the screen. Good for non-moving background elements.
	"""
        layer = StaticLayer()
        layer.enable_camera(camera)
	if depth is None:
	    try:
		depth = max(self.layers.itervalues())[0]+1
	    except ValueError:
		depth = 0
        self.layers[name] = [depth, layer]
        self._reorder()
        return layer

    def clear_nonstatic(self):
        """clear_nonstatic() -> None
	
	Clear all non-static layers.
	"""
        for d,l in self.layers.itervalues():
            if not isinstance(l, StaticLayer):
                l.clear()

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


    ######################
    ##  Entity Methods  ##
    ######################
    
    def add_all(self, layername, entitylist):
	"""add_all(layername, entitylist) -> None
	
	Add all entities from a list to the given layer.
	"""
        layer = self.layers[layername][1]
        for e in entitylist:
            e.attach_to(layer)
    
    def add(self, layername, entity):
	"""add(layername, entity) -> Entity
	
	Add an entity to the given layer.
	"""
        layer = self.layers[layername][1]
        entity.attach_to(layer)
        return entity

    def remove(self, entity):
	"""remove(entity) -> None
	
	Remove an entity from the scene.
	"""
        entity.detach()

    def remove_all(self, entitylist):
	"""remove_all(entitylist) -> None
	
	Remove all listed entities from the scene.
	"""
        for e in entitylist:
            e.detach()

    def __iter__(self):
        for d,l in self.depth_cache:
            for e in l:
                yield e


    def pick(self, x, y, layer=None):
	"""Pick the foremost entity from the given screen coordinates.
	Layer name can be given as an optional parameter to restrict
	the search to a single layer.
	"""
	pass
		

    ###################
    ##  Misc Methods  #
    ###################

    def set_collision_handler(self, group1, group2, handler):
        self.coll.set_handler(group1, group2, handler)

    def clear_collnodes(self):
        self.coll.clear_nodes()

    def make_entity(self):
	"""make_entity -> Entity
	
	Create an entity from the whole scene that can be used to
	draw (a static version) of the scene on another scene.
	"""
        s = GLShape()
        s._listid = glGenLists(1)
        glNewList(s._listid, GL_COMPILE)
        for e in self:
            e._execute()
        glEndList()
        return Entity(s)

    def draw(self):
	"""draw() -> None
	
	Draw all layers in z-order to the screen.
	"""
        for d,l in self.depth_cache:
            if l.camera:
                glPushMatrix()
                glScalef(self.zoom, self.zoom, 1)
                glTranslatef(-self.offset[0], -self.offset[1], 0)
            l.draw()
            if l.camera:
                glPopMatrix()

    def _reorder(self):
        self.depth_cache = self.layers.values()
        self.depth_cache.sort()            

class Layer(Node):
    camera = True
    
    def __init__(self):
        Node.__init__(self)
        self._fast_draw = Set()
        self._slow_draw = Set()

    def draw(self, director=director,
             glPushMatrix=glPushMatrix,
             glTranslatef=glTranslatef,
             glRotatef=glRotatef,
             glScalef=glScalef,
             glColor4f=glColor4f,
             glPopMatrix=glPopMatrix):
        for e in self._fast_draw:
            if e.hidden or e.shape is None:
                continue
            glPushMatrix()
            glTranslatef(e.x, e.y, 0)
            glRotatef(e.angle, 0,0,1)
            scale = e.scale
            if type(scale) is not tuple:
                scale = (scale,scale)
            glScalef(scale[0],scale[1],0)
            color = e.color
            if color is not None:
                glColor4f(*_conv_color(*color))
            else:
                glColor4f(1,1,1,1)
            e.shape._draw()
            e.realx = e.x
            e.realy = e.y
            if director.ticker.realtick:
                if scale == 1 and self.angle == 0:
                    for n in e._collision_nodes:
                        n.realx, n.realy = e.realx+n.x, e.realy+n.y
                else:
                    ox,oy = director.scene.offset
                    for n in e._collision_nodes:
                        if n.x == 0 and n.y == 0:
                            n.realx = e.realx
                            n.realy = e.realy
                        else:
                            n.realx, n.realy = project_point(n.x, n.y)
                            n.realx += ox
                            n.realy += oy
            glPopMatrix()
        for e in self._slow_draw:
            e.traverse()
       
    def clear(self):
        self._fast_draw.clear()
        self._slow_draw.clear()
        Node.clear(self)

    def enable_camera(self, flag=True):
        self.camera = flag

    def _attach(self, other, front=True):
        Node._attach(self, other)
        if other.fast_draw:
            self._fast_draw.add(other)
        else:
            self._slow_draw.add(other)

    def _detach(self, other):
        Node._detach(self, other)
        self._fast_draw.discard(other)
        self._slow_draw.discard(other)


class StabileLayer(Layer):
    
    def __init__(self):
        Node.__init__(self)
        self._fast_draw = []
        self._slow_draw = []

    def clear(self):
        del self._fast_draw[:]
        del self._slow_draw[:]
        Node.clear(self)

    def _attach(self, other, front=True):
        Node._attach(self, other)
        if other.fast_draw:
            self._fast_draw.append(other)
        else:
            self._slow_draw.append(other)

    def _detach(self, other):
        Node._detach(self, other)
        try:
            self._fast_draw.remove(other)
        except:
            pass
        try:
            self._slow_draw.remove(other)
        except:
            pass


class StaticLayer(Layer):
    def __init__(self):
        Layer.__init__(self)
        self.listid = None
        self._layer_uptodate = False


    def _attach(self, child, front=True):
        Node._attach(self, child)
        self._layer_uptodate = False

    def _detach(self, child):
        Node._detach(self, child)
        self._layer_uptodate = False

    def clear(self):
        Layer.clear(self)
        self._layer_uptodate = False
        
    def compile(self):
        if self.listid is None:
            self.listid = glGenLists(1)
        glNewList(self.listid, GL_COMPILE)
        for e in self.fchildren:
            e.traverse()
        glEndList()
        self._layer_uptodate = True

    def draw(self):
        if not self._layer_uptodate:
            self.compile()
        glCallList(self.listid)

    def uncompile(self):
        if self.listid is None:
            return
        if glDeleteLists is None:
            return
        glDeleteLists(self.listid, 1)

    def __del__(self):
        self.uncompile()

