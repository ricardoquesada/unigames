"""Entity actions

Actions are autonomous mutators for Entity objects that can be
chained to easily program movement and animation behavior.
"""

import pygame
from pygame.locals import Rect

from pygext.gl.director.animation import *
from pygext.gl.director.globals import director
from pygext.gl.director.entities import Entity
from pygext.color import _conv_color, _blend
from pygext.math.vecalg import sincos

from copy import copy

try:
    Set = set
except NameError:
    from sets import Set

try:
    from psyco.classes import *
except:
    pass

__all__ = [
    "Action",
    "IntervalAction",
    
    "MoveDelta",
    "MoveTo",
    "Move",
    "MoveForward",
    
    "Animate",

    "CallFunc",
    "CallFuncE",

    "TickFunc",
    "RealTickFunc",
    
    "Delete",
    "Delay",
    "SetAttr",
    "CreateAnim",
    "Blink",
    "ColorFade",
    "AlphaFade",
    "Rotate",
    "RotateDelta",
    "Scale",
    "SetState",
    "SetScene",
    "Fork",
    "Repeat",

    "Hide",
    "Show",

    "StopMode",
    "RepeatMode",
    "PingPongMode",
    ]

class Action(object):
    """Abstract base class for actions"""

    def __init__(self, *arg, **kw):
        self.next = None
        self.next_kw = {}
        self.timelimit = None
        self.arealimit = None
        self.slaves = Set()  ## actions dependant on this action
        self.ended = False
        self.init(*arg, **kw)

    def init(self):
        """Called when the action object is created. Override in subclass."""
        pass ## override

    def cleanup(self):
        """Called when the action ends. Override in a subclass."""
        pass ## override

    def start(self):
        """Called when the action is initiated on an entity. Override in subclass."""
        pass ## override

    def action(self):
        """Called once per tick to perform the action action. Override in subclass."""
        pass ## override


    def do(self, entity=None, **kw):
	"""Perform this action for an entity or node.
	
	This method creates a copy of the Action object and attatches it
	to the given entity. The copied Action is also registered to the
	global Director so that it will be called each frame.
	
	@return the copied Action attatched to the Entity
	"""
        reactor = director.reactor
        ticker = director.ticker
        obj = self.__class__.__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj.entity = entity
        obj.starttime = ticker.now
        reactor.add(obj)
        if entity is not None:
            entity.current_actions.add(obj)
        obj.start(**kw)
        return obj

    def __radd__(self, action):
        if isinstance(action, type):
            action = action()
        else:
            action = copy(action)
        return action.chain(self)

    def __add__(self, action):
        if isinstance(action, type):
            action = action()
        obj = copy(self)
        return obj.chain(action)

    def __iadd__(self, action):
        if isinstance(action, type):
            action = action()
        return self.chain(action)        

    def endwith(self, action):
	"""Limit this action by another action.
	
	This method links this action to the given action so that as soon as
	the target action ends, this action will end too.
	"""
        if not hasattr(action, entity):
            raise ValueError, "You can only link to actions that are being performed using endwith()"
        action.slaves.add(self)
        return self

    def chain(self, action, **kw):
	"""Chain a new action that will be started when this action ends.
	"""
	if action is self:
            raise ValueError, "can't chain an action to itself"
        if self.next is not None:
            self.next = copy(self.next).chain(action, **kw)
        else:
            self.next = action
            self.next_kw = kw
        return self

    def limit(self, time=None, area=None):
	"""Set the ending criteria fod this action.
	
	This method will set a time or area limit for the action. The
	time limit is given in seconds, and the area is a rect-style
	object that triggers action.end() if the entity attatched to
	the action leaves the rect.
	"""
        if time is not None:
            self.timelimit = time
        if area is not None:
            self.arealimit = Rect(area)
        return self

    def tick(self):
        t = director.ticker
        if t.realtick:
            if self.entity is not None and self.entity.deleted:
                self.end()
                return
            if self.arealimit is not None:
                if not self.arealimit.collidepoint(self.entity.x, self.entity.y):
                    self.end()
                    return
            self.action()
            if self.timelimit is not None:
                if t.next_realtick >= self.starttime + self.timelimit * 1000:
                    self.end()
                    return
        else:
            self.action()

    def abort(self):
	"""End this action immediately and do NOT continue to the next in chain.
	"""
        if self.ended:
            return
        director.reactor.remove(self)
        if self.entity is not None:
            self.entity.current_actions.discard(self)
            self.entity = None
        self.ended = True
        self.cleanup()
        for slave in self.slaves:
            slave.end()

    def end(self):
	"""End this action and proceed to the next one in chain.
	"""
        entity = self.entity
        self.abort()
        if self.next is not None and (entity is None or not entity.deleted):
            obj = self.next.do(entity, **self.next_kw)
            return obj

    def __repr__(self):
        return "<%s at %i>: %r" % (self.__class__.__name__, id(self), self.entity)

def makef(tr, ts, func=None):
    """
    Create a function that fulfills the following criteria

    f'(t) = 0..c when t = (0..tr)
    f'(t) = c    when t = (tr..ts)
    f'(t) = c..0 when t = (ts..1)
    f(0) = 0
    f(1) = 1
    """
    if tr < 0:
        tr = 0
    if tr > 1:
        tr = 1
    if ts > 1:
        ts = 1
    if ts < tr:
        ts = tr
    c = 2.0/(ts-tr+1)
    c2 = 0.5*c
    if tr > 0:
        c2tr = c2/tr
    trc2 = tr*c2
    if ts < 1.0:
        d = (1-ts)
        cd = c/d
        c2d = -c2/d
    if func is None:
        def f(t):
            if t < tr:
                return c2tr*t*t
            elif t > ts:
                return c2d*t*t+cd*t+c2d+1
            else:
                return c*t-trc2
    else:
        def f(t):
            t = func(t)
            if t < tr:
                return c2tr*t*t
            elif t > ts:
                return c2d*t*t+cd*t+c2d+1
            else:
                return c*t-trc2
        
    return f


def stop_func(x):
    return min(x, 1.0)

def repeat_func(x):
    return x % 1.0

def pingpong_func(x):
    x %= 2.0
    if x > 1.0:
        return 1.0 - x % 1.0
    return x

class StopMode: pass
class RepeatMode: pass
class PingPongMode: pass

funcs = {
    StopMode: stop_func,
    RepeatMode: repeat_func,
    PingPongMode: pingpong_func,
    }

legacymapper = {
    StopMode: "stop",
    RepeatMode: "repeat",
    PingPongMode: "pingpong",
    }

class IntervalAction(Action):
    """Abstract base class for linear actions.
    
    "Interval" action means an action that has a clearly defined
    beginning and ending point, so that it can be repeated. The
    repeat modes are:
	
    StopMode     - Don't repeat. Stop after first round.
    RepeatMode   - Repeat from beginning.
    PingPongMode - Every other repetition is done backwards (useful for animations and movement)
    """

    fadein = None
    fadeout = None

    def start(self):
        secs = self.secs * 1000
        self.endtime = self.starttime + secs
        self.timelen = float(secs)
        self.timefunc = funcs[self.mode]
        if self.fadein is not None:
            self.fadein = self.fadein*1000.0 / self.timelen
        else:
            self.fadein = 0.0
        if self.fadeout is not None:
            self.fadeout = 1.0 - (self.fadeout*1000.0 / self.timelen)
        else:
            self.fadeout = 1.0
        if self.fadein > 0.0 or self.fadeout < 1.0:
            f = makef(self.fadein, self.fadeout, func=self.timefunc)
            self.timefunc = f

    def smooth(self, fadein=None, fadeout=None):
        self.fadein = fadein
        self.fadeout = fadeout
        return self

    def action(self):
        t = director.ticker
        now = t.now
        if self.mode is StopMode and t.next_realtick >= self.endtime:
            now = t.next_realtick
            x = (now - self.starttime) / self.timelen
            self.limited(self.timefunc(x))
            self.end()
        else:
            x = (now - self.starttime) / self.timelen
            self.limited(self.timefunc(x))


class Hide(Action):
    """Hide the current entity"""
    def start(self):
        self.entity.hidden = True
        self.end()

class Show(Action):
    """Show the current entity"""
    def start(self):
        self.entity.hidden = False
        self.end()

class Fork(Action):
    """Fork a new action
    
    Usually chained actions wait for the previous action to end
    before activating, but Fork can be used to trigger an action
    and then immediately move to the next action in the chain.
    """
    def init(self, *actions):
        self.actions = actions

    def start(self):
        for action in self.actions:
            action.do(self.entity)
        self.end()

class Repeat(Action):
    """Repeat an action several times
    """
    def init(self, action, times=None):
        self.target = action
        self.times = times

    def start(self):
        self.index = 0
        self.repeats = self.times
        self.target.chain(CallFunc(self._goto_next))
        act = self.target.do(self.entity)
        #act.chain(CallFunc(self._goto_next))

    def _goto_next(self):
        if self.entity is not None and self.entity.deleted:
            self.end()
            return
        if self.times is not None:
            self.repeats -= 1
            if self.repeats == 0:
                self.end() # TODO: repeat
                return
        act = self.target.do(self.entity)
        #act.chain(CallFunc(self._goto_next))

class SetState(Action):
    """Set the state of the current Scene
    """
    def init(self, state):
        self.state = state

    def start(self):
        director.scene.set_state(self.state)
        self.end()

class SetScene(Action):
    """Transition to a new Scene
    """
    def init(self, scene, *arg, **kw):
        self.scene = scene
        self.arg = arg
        self.kw = kw

    def start(self):
        director.set_scene(self.scene, *self.arg, **self.kw)
        self.end()

class ColorFade(IntervalAction):
    """Smoothly fade the entity from current color to a new color
    """
    
    def init(self, targetcolor, secs, mode=StopMode):
        self.targetcolor = targetcolor
        self.secs = secs
        self.mode = mode

    def start(self):
        IntervalAction.start(self)
        self.startcolor = self.entity.color or (255,255,255,255)

    def limited(self, x):
        self.entity.color = _blend(self.startcolor, self.targetcolor, x)

class AlphaFade(ColorFade):

    def init(self, targetalpha, secs, mode=StopMode):
        self.targetalpha = targetalpha
        self.secs = secs
        self.mode = mode

    def start(self):
        ColorFade.start(self)
        r,g,b,a = self.startcolor
        self.targetcolor = (r,g,b,self.targetalpha)

class Blink(Action):
    """Alternate the entity between hidden and visible state
    """
    def init(self, visible_time, hidden_time=None, repeats=None):
        if hidden_time is None:
            hidden_time = visible_time
        self.visible_time = visible_time
        self.hidden_time = hidden_time
        self.repeats = repeats

    def start(self):
        self.hidden = True
        self.entity.hidden = True
        self.next_swap = director.ticker.now + self.hidden_time * 1000
        self.count = 0

    def action(self):
        now = director.ticker.now
        if now > self.next_swap:
            if self.hidden:
                self.count += 1
                self.hidden = False
                self.entity.hidden = False
                if self.repeats and self.count >= self.repeats:
                    self.end()
                    return
                self.next_swap = now + self.visible_time * 1000
            else:
                self.hidden = True
                self.entity.hidden = True
                self.next_swap = now + self.hidden_time * 1000

def CreateAnim(layer, x, y, frames, secs):
    """
    Creates a new entity that plays the given animation, then deletes itself.
    """
    action = Create(layer, Entity) + SetAttr(x=x,y=y) + Animate(frames, secs) + Delete
    return action

class Create(Action):
    """Create a new entity
    
    If the action chain already has a current entity, the created entity
    will be placed in the same x,y position.
    """
    def init(self, layer, entitycls, *arg, **kw):
        self.cls = entitycls
        self.arg = arg
        self.kw = kw
        self.layer = layer

    def start(self, **kw):
	old = self.entity
        self.entity = self.cls(*self.arg, **self.kw)
	if old is not None:
	    self.entity.x = old.realx
	    self.entity.y = old.realy
        self.entity.place(self.layer)
        if kw:
            self.entity.set(**kw)
        self.end()

class SetAttr(Action):
    """Set an attribute in the current entity"""
    def init(self, **kw):
        self.kw = kw

    def start(self):
        self.entity.set(**self.kw)
        self.end()

class Delay(Action):
    """Delay for x seconds"""
    def init(self, delay):
        self.delay = delay

    def start(self):
        self.endtime = self.starttime + self.delay * 1000
    
    def tick(self):
        if director.ticker.now >= self.endtime:
            self.end()
        

class Delete(Action):
    """Delete the current entity
    """
    def start(self):
        if self.entity is not None and not self.entity.deleted:
            self.entity.delete()
        self.end()

class CallFunc(Action):
    """Call a function
    """
    def init(self, func, *arg, **kw):
        self.func = func
        self.arg = arg
        self.kw = kw

    def start(self):
        self.func(*self.arg, **self.kw)
        self.end()

class CallFuncE(CallFunc):
    """Call a function with the current entity as first parameter
    """
    def start(self):
        self.func(self.entity, *self.arg, **self.kw)
        self.end()

class TickFunc(Action):
    def init(self, func):
        self.func = func

    def action(self):
        self.func(self.entity)

class RealTickFunc(TickFunc):
    def action(self, ticker=director.ticker):
        if ticker.realtick:
            self.func(self.entity)


class Animate(Action):
    """Animate the current entity
    """
    def init(self, frames, secs, mode=StopMode):
        self.frames = frames
        self.secs = secs
        self.mode = legacymapper[mode]

    def start(self):
        self.animator = EntityAnimator(self.entity, self.frames, self.secs, mode=self.mode)
        self.endtime = self.starttime + self.secs * 1000
        self.entity.shape = self.frames[0]

    def action(self):
        self.animator.tick()
        if self.mode == "stop" and director.ticker.now >= self.endtime:
            self.end()

class Rotate(Action):
    """Rotate the current entity with a given speed"""
    def init(self, anglev):
        self.anglev = anglev

    def set_velocity(self, anglev):
        self.anglev = anglev

    def add_velocity(self, anglev):
        self.anglev += anglev

    def mul_velocity(self, m):
        self.anglev *= m

    def action(self, ticker=director.ticker):
        delta = ticker.tick_delta
        self.entity.angle += self.anglev * delta

class RotateDelta(IntervalAction):
    """Rotate the current entity by the given degrees"""
    def init(self, angle, secs, mode=StopMode):
        self.angle = angle
        self.mode = mode
        self.secs = secs

    def start(self):
        IntervalAction.start(self)
        self.startang = self.entity.angle

    def limited(self, x):
        self.entity.angle = self.startang + self.angle * x

class Scale(IntervalAction):
    """Enlarge or shrink the current entity"""
    def init(self, scale, secs, mode=StopMode):
        self.scale = scale
        self.secs = secs
        self.mode = mode

    def start(self):
        IntervalAction.start(self)
        self.startscale = self.entity.scale
        self.dscale = self.scale - self.startscale

    def limited(self, x):
        self.entity.scale = self.startscale + self.dscale * x
        

class Move(Action):
    """Move the current entity with the given velocity"""
    def init(self, vx, vy):
        self.vx = vx
        self.vy = vy

    def set_velocity(self,vx,vy):
        self.vx = vx
        self.vy = vy

    def add_velocity(self,vx,vy):
        self.vx += vx
        self.vy += vy

    def mul_velocity(self,mx,my):
        self.vx *= mx
        self.vy *= my

    def action(self, ticker=director.ticker):
        delta = ticker.tick_delta
        self.entity.x += self.vx * delta
        self.entity.y += self.vy * delta

class MoveDelta(IntervalAction):
    """Move the current entity by the given x,y delta"""
    def init(self, dx, dy, secs, mode=StopMode):
        self.dx = dx
        self.dy = dy
        self.secs = float(secs)
        self.mode = mode

    def start(self):
        IntervalAction.start(self)
        self.startx = self.entity.x
        self.starty = self.entity.y

    def limited(self, x):
        self.entity.x = self.startx + x * self.dx
        self.entity.y = self.starty + x * self.dy

class MoveTo(MoveDelta):
    """Move the current entity to the given x,y position
    """
    def init(self, targetx, targety, secs, mode=StopMode):
        self.targetx = targetx
        self.targety = targety
        self.secs = float(secs)
        self.mode = mode

    def start(self):
        self.dx = self.targetx - self.entity.x
        self.dy = self.targety - self.entity.y
        MoveDelta.start(self)

class MoveForward(Action):
    def init(self, velocity=0):
        self.velocity = velocity

    def action(self, ticker=director.ticker):
        delta = ticker.tick_delta
        vx,vy = sincos(self.entity.angle, self.velocity * delta)
        self.entity.x += vx
        self.entity.y += vy
