"""Director base class implementation
"""

import pygame
from pygame.locals import *
import gc

try:
    Set = set
except NameError:
    from sets import Set

try:
    from psyco.classes import *
except:
    pass

__all__ = [
    "Director",
    ]

class Director(object):
    """Scene director

    The director is the element that controls the main loop
    and calls event handlers, updates actions etc. You should
    not create instances of this class manually, as the default
    instance is automatically initialized in pygext.gl.director.globals,
    and other components depend on that instance.
    """
    
    def __init__(self, resolution=40):
        from pygext.gl.director.reactor import Reactor, Ticker
        self.reactor = Reactor()
        self.ticker = Ticker(resolution=resolution)
        #self.collisions = Set()
        self.scene = None
        self.next_scene = None
        self.running = True
        self.gui_root = None

        self.visible_collision_nodes = False

    def init_gui(self):
        if self.gui_root is None:
            from pygext.gl.gui.root import Root
            self.gui_root = Root()
        return self.gui_root

    def run(self, initial_scene, *arg, **kw):
        """Launch the director mainloop.

        initial_scene - Scene class or instance that will be the first entered scene
        """
        from pygext.gl import screen
        from pygext.gl.mouse import glmouse

        start_time = pygame.time.get_ticks()
        realticks = 0
        ticks = 0

        self.ticker.tick()
        self.set_scene(initial_scene, *arg, **kw)
        while self.running:
            if self.next_scene is not None:
                s,a,kw = self.next_scene
                self._set_scene(s, *a, **kw)
            gui = self.gui_root
            screen.clear()
            self.scene.draw()
            if self.visible_collision_nodes:
                self.scene.coll.draw_nodes()
                gc.collect()
            mx,my = pygame.mouse.get_pos()
            mx *= screen.xmult
            my *= screen.ymult
            glmouse.x = mx
            glmouse.y = my
            if gui is not None:
                self.gui_root.traverse()
            ptr = glmouse.pointer
            if ptr is not None:
                ptr.x = mx
                ptr.y = my
                ptr.traverse()
            screen.flip()
            self.ticker.tick()
            if self.ticker.realtick:
                if self.scene.coll:
                    self.scene.coll.check_collisions()
                events = pygame.event.get()
                self.scene.handle_events(events)
                if gui is not None:
                    gui.tick()
                    gui.handle_events(events)
                realticks += 1
                self.realtick_func()
            self.tick_func()
            self.reactor.tick()
            #pygame.time.wait(1) # to reduce CPU usage
            ticks += 1

        end_time = pygame.time.get_ticks()
        secs = (end_time-start_time)/1000.0

        self.secs = secs
        self.ticks = ticks
        self.realticks = realticks

    def quit(self):
        """Exit from the director's mainloop.
        """
        self.running = False

    def set_state(self, state):
        self.state = state
        tick = self.scene.tick
        if state is not None:
            func = getattr(self.scene, "state_%s_tick" % self.scene.state, None)
            if func:
                tick = func
            
        self.tick_func = tick
            
        realtick = self.scene.realtick
        if state is not None:
            func = getattr(self.scene, "state_%s_realtick" % self.scene.state, None)
            if func:
                realtick = func
            
        self.realtick_func = realtick

    def set_scene(self, scene, *arg, **kw):
        self.next_scene = (scene, arg, kw)

    def _set_scene(self, scene, *arg, **kw):
        """Change to a new scene.
        """
        self.next_scene = None
        from pygext.gl.director.reactor import Reactor
        gc.collect()
        if gc.garbage:
            print "WARNING: your application produced %i items of garbage" % len(gc.garbage)
            print gc.garbage[:25]
        #self.print_obj_stats()
        if self.scene is not None:
            self.scene.exit()
            for name,layer in self.scene.layers.items():
                layer[1].clear()
                self.scene.del_layer(name)
        self.reactor = Reactor()
        gc.collect()
        if self.gui_root:
            self.gui_root.clear()
            self.gui_root = None
        if isinstance(scene, type):
            self.scene = scene = scene.__new__(scene)
            scene.__init__()
        else:
            self.scene = scene
        self.set_state(None)
        scene.enter(*arg, **kw)
        pygame.event.clear()
        pygame.event.set_allowed(None)
        events = scene.event_handler.keys()
        if events:
            pygame.event.set_allowed(events)
        if self.gui_root:
            pygame.event.set_allowed([MOUSEBUTTONDOWN,MOUSEBUTTONUP])
                    
