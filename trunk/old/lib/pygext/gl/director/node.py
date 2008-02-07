"""Node in the scene graph
"""

__all__ = [
    "Node",
    ]

try:
    Set = set
except NameError:
    from sets import Set

try:
    from psyco.classes import *
except:
    pass


#import weakref
from OpenGL.GL import glPushMatrix, glPopMatrix, glTranslatef, glScalef, glRotatef, glLoadIdentity

from pygext.gl.transform import IdentityTransform, project_point, project_polygon, project_rect
from pygext.gl.director.globals import director
from pygame.locals import Rect

class Node(object):
    """A single scene-graph node

    Each node has the basic properties to control its
    position and orientation. All these properties are
    relative to the node's parent.

    node.x     - horizontal position
    node.y     - vertical position
    node.angle - rotation in degrees
    node.scale - size scales

    In addition, each node has the attributes realx and realy which
    contain the node's absolute position on the screen.
    """
    
    fast_draw = False

    def __init__(self):
        ## TODO: As a memory optimization, all Set attributes could
        ##       be None on initialization, and created lazily when
        ##       needed.
        self.parent = None
        self.fchildren = Set()
        self.bchildren = Set()
        self.deleted = False
        self.hidden = False
        self.current_actions = Set()
        self.realx = 0
        self.realy = 0

        self._collision_nodes = Set()

        self.x = 0
        self.y = 0
        self.scale = 1
        self.angle = 0

    def abort_actions(self, typefilter=None):
        """abort_actions([typefilter]) -> None
        
        End all current actions (if any) and do NOT proceed to
        any new actions. If typefilter is given, only actions of
        that type (and its subclasses) are aborted.
        """
        for a in list(self.current_actions):
            if typefilter is None or isinstance(a, typefilter):
                a.abort()

    def end_actions(self, typefilter=None):
        """end_actions([typefilter]) -> None
        
        End all current actions and proceed to the next actions
        in the action chains. If typefilter is given, only action
        of that type (and its subclasses) are ended.
        """
        for a in list(self.current_actions):
            if typefilter is None or isinstance(a, typefilter):
                a.end()

    def get_actions(self, typefilter=None):
        """Get a list of currently active actions from this Node"""
        return [a for a in list(self.current_actions)
                if typefilter is None or isinstance(a, typefilter)]

    def do(self, *actions, **kw):
        """do(*actions) -> this
        
        Begin performing a new action(s) on this entity.
        """
        for action in actions:
            if isinstance(action, type):
                action = action()
            action.do(self, **kw)
        return self

    def delete(self):
        """delete() -> None

        Delete this node from the graph
        """
        self.detach()
        self._delete()

    def _delete(self):
        self.deleted = True
        self._collision_nodes.clear()
        for c in self:
            c._delete()
        self.parent = None
        self.fchildren.clear()
        self.bchildren.clear()

    def attach_to(self, node, back=False):
        """attach_to(node) -> None

        Attach this node as a child of target node.
        """
        if self.parent is not None:
            self.detach()
        #self.parent = weakref.proxy(node)
        self.parent = node
        node._attach(self, back)
        return self

    def detach(self):
        """detach() -> None

        Detach this node from its parent
        """
        if self.parent is None:
            return
        self.parent._detach(self)
        self.parent = None
        return self

    def add_collnode(self, group, *arg, **kw):
        director.scene.coll.add_node(group, self, *arg, **kw)

    def clear_collnodes(self):
        self._collision_nodes.clear()

    def clear(self):
        """clear() -> None

        Remove all children from this node
        """
        for c in self:
            c._delete()
        self.fchildren.clear()
        self.bchildren.clear()

    def traverse(self):
        """traverse() -> None

        Traverse down this node in the scene-graph.
        """
        if self.hidden:
            return        
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        self._draw_here()
        glPopMatrix()

    def _draw_here(self):
        glRotatef(self.angle, 0,0,1)
        scale = self.scale
        if type(scale) is not tuple:
            scale = (scale,scale)
        glScalef(scale[0],scale[1],0)
        if director.ticker.realtick:
            ox,oy = director.scene.offset
            self.realx, self.realy = project_point(0,0)
            self.realx += ox
            self.realy += oy
            for n in self._collision_nodes:
                n.realx, n.realy = project_point(n.x, n.y)
                n.realx += ox
                n.realy += oy
        filter(Node.traverse, self.bchildren)
        self.enter()
        filter(Node.traverse, self.fchildren)
        self.exit()
        

    def enter(self):
        """enter() -> None

        Called when entering this node in graph traversal
        """
        pass

    def exit(self):
        """exit() -> None

        Called when exiting this node in graph traversal
        """
        pass

    def __iter__(self):
        for c in self.fchildren:
            yield c
        for c in self.bchildren:
            yield c

    def __len__(self):
        return len(self.fchildren)+len(self.bchildren)

    def __nonzero__(self):
        return True


    def transform_polygon(self, poly):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0,0,1)
        scale = self.scale
        if type(scale) is not tuple:
            scale = (scale,scale)
        glScalef(scale[0],scale[1],0)
        p = project_polygon(poly)
        glPopMatrix()
        return p

    def transform_rect(self, rect):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.angle, 0,0,1)
        scale = self.scale
        if type(scale) is not tuple:
            scale = (scale,scale)
        glScalef(scale[0],scale[1],0)
        r = project_rect(rect)
        glPopMatrix()
        return r
        

    def _attach(self, child, back=False):
        if not back:
            self.fchildren.add(child)
        else:
            self.bchildren.add(child)

    def _detach(self, child):
        self.fchildren.discard(child)
        self.bchildren.discard(child)

