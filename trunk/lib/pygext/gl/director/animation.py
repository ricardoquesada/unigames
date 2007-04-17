"""Entity animation utilities

This module contains utility classes to move and animate entities
independently of the current framerate. Usually you don't need to
use these classes directly. See pygext.gl.director.actions for a
more high-level API.
"""

import pygame

from pygext.gl.director.globals import director
from pygext.gl.resources import resources

try:
    from psyco.classes import *
except:
    pass

__all__ = [
    'EntityAnimator',    
    ]

class EntityAnimator(object):
    def __init__(self, entity, frames, secs, first_frame=0, mode="stop"):
        self.entity = entity
        if isinstance(frames, basestring):
            frames = resources.get_anim(frames)
        self.frames = frames
        self.secs = secs
        self.first = True
        self.len = len(frames)
        self.first_frame = first_frame
        self.first_time = 0
        self.ms_per_frame = secs * 1000.0 / self.len
        if mode == "repeat":
            self.index_func = self.repeat_func
        elif mode == "pingpong":
            self.index_func = self.pingpong_func
        else:
            self.index_func = self.stop_func
            

    def tick(self, ticker=director.ticker):
        now = pygame.time.get_ticks()
        if self.first:
            self.first = False
            self.entity.shape = self.frames[self.first_frame]
            self.first_time = now
        else:
            index = self.index_func(now)
            self.entity.shape = self.frames[index]
            

    def stop_func(self, now):
        index = (now - self.first_time) // self.ms_per_frame + self.first_frame
        return min(int(index), self.len-1)

    def repeat_func(self, now):
        index = (now - self.first_time) // self.ms_per_frame + self.first_frame
        return int(index) % self.len

    def pingpong_func(self, now):
        index = (now - self.first_time) // self.ms_per_frame + self.first_frame
        index = int(index)
        l = self.len-1
        i = (index % (l*2))
        if i > l:
            i = l - (index % l)
        return i
