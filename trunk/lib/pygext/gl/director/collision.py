"""Collision Handling.

This module contains the classes for automatic, radius-based collision detection.
Your application should create one or more CollisionHandler objects and attatch
objects to them.
"""
import weakref
import Numeric as N
from pygext.gl.director.globals import director
from pygext.gl.director.node import Node
from pygext.gl.shapes.simple import circle
from OpenGL.GL import glColor4f

##try:
##    from psyco.classes import *
##except:
##    pass

__all__ = [
    'RadialCollisions',
    ]

class CollisionNode(object):
    """Scenegraph node that is used for collision checking.
    
    Collision nodes typically have only the x and y properies
    and not other transformations. Also, for optimization
    reasons, collision nodes can't have child nodes.
    """
    
    __slots__ = ("parent", "x", "y", "realx", "realy")
    
    def __init__(self, parent, x, y):
        self.x = x
        self.y = y
        self.parent = weakref.proxy(parent)
        #self.parent = parent
        self.realx = 0
        self.realy = 0
        

class CollisionHandler(object):
    """Abstract base clasee for collision handlers"""
    
    
    def add_node(self, groupname, parent, *arg, **kw):
        """abstract method implemented in subclasses"""
        raise NotImplemented
        
class RadialCollisionNode(CollisionNode):
    """Collision node based on a radius.
    
    Checks for collisions using a circle shaped area.
    """
       
    def __init__(self, parent, radius=None, x=0, y=0):
        if radius is None:
            if hasattr(parent, "shape") and parent.shape is not None:
                r = parent.shape.bounding_rect
                x,y = r.center
                size = max(r.width, r.height)
                radius = size / 2.0
            else:
                radius = 0
        CollisionNode.__init__(self, parent, x, y)
        self.radius = radius

    def draw(self):
        circle(self.radius).fillcolor(255,255,255,100).translate(self.x,self.y).execute()
        
        

class RadialCollisions(object):
    """Collision handler for circle-shaped objects
    
    All entities registered to this handler must have their
    collision mask made up from one or more circles.
    """
    
    def __init__(self):
        self.groups = {}
        self.handlers = {}
        
    def add_node(self, groupname, parent, radius=None, x=0, y=0):
        """Add a new collision node for an entity.
        
        groupname - name for the collision group, used for registering handler functions
        parent    - parent Node to attach the collision node to
        radius    - size of the collision circle
        x,y       - position of the collision circle
        
        If radius,x and y are not specified, the method tries to calculcate
        a suitable collision circle by using the Entity's shape's
        bounding rect.
        
        Note that a single entity CAN have several collision circles
        to accomodate non-circular shapes.
        """
        node = RadialCollisionNode(parent, radius, x, y)
        if isinstance(parent, Node):
            parent._collision_nodes.add(node)
        try:
            group = self.groups[groupname]
        except KeyError:
            group = weakref.WeakKeyDictionary()
            self.groups[groupname] = group
        group[node] = True
        return node

    def set_handler(self, group1, group2, func):
        """Set the collision handler function for two groups.
        
        Register the function that will be called when entities from the
        specified groups collide. For performance, it is more efficient
        to specify the groups in few-to-many order. For example,
        
        set_handler(self, "player", "enemies", player_collide)
        """
        self.handlers[(group1,group2)] = func

    def start(self):
        """Start checking for collisions automatically every tick.
        """
        director.collisions.add(self)
        
    def stop(self):
        """Stop the automatic collision detection.
        """
        director.collisions.remove(self)

    def draw_nodes(self):
        glColor4f(1,1,1,0.4)
        for g in self.groups.itervalues():
            for n in g:
                circle(n.radius).translate(n.realx,n.realy).execute()

    def clear_nodes(self):
        self.groups = {}

    def check_collisions(self):
        """Check for collisions and call all registered collision functions.
        """
        for (g1,g2),func in self.handlers.iteritems():
            nodes1 = list(self.groups.get(g1,[]))
            nodes2 = list(self.groups.get(g2,[]))
            if not nodes1 or not nodes2:
                continue

#            if len(nodes1) > len(nodes2):
#                nodes1,nodes2 = nodes2,nodes1

            n = len(nodes2)
            x = N.zeros(n, N.Float32)
            y = N.zeros(n, N.Float32)
            r = N.zeros(n, N.Float32)
            for i,n in enumerate(nodes2):
                x[i] = n.realx
                y[i] = n.realy
                r[i] = n.radius

            for n in nodes1:
                dx = x-n.realx
                dy = y-n.realy
                dr = r+n.radius
                dx *= dx
                dy *= dy
                dr *= dr
                collision = dx+dy <= dr
                for i in N.nonzero(collision):
##                    print "collision %s to %s" % (g1,g2)
##                    print n.parent, nodes2[i].parent
##                    print n.parent.realx,n.parent.realy
##                    print nodes2[i].parent.realx, nodes2[i].parent.realy
                    func(n.parent, nodes2[i].parent)
                        
try:
    import psyco
    psyco.bind(RadialCollisions.check_collisions)
except ImportError:
    pass
