"""Event reactor
"""

ITERATE_REACTOR_COPY = False

import pygame

try:
    Set = set
except NameError:
    from sets import Set

try:
    from psyco.classes import *
except:
    pass

__all__ = [
    'Ticker',
    'Reactor',
    ]

class Ticker(object):
    """Framerate independent timer
    
    Utility class for event timing. The idea is that a "tick" happens
    once every frame, and a "realtick" happens only as dictated by
    the resolution of the timer. Useful attribute in this class:
	
    last_realtick - time when the last realtick took place (as returned by pygame.time.get_ticks())
    next_realtick - when the next realtick should happen
    now           - current time
    delta         - amount of time from the last tick (in seconds)
    realtick      - boolean value: is the current tick a realtick?
    """
    
    def __init__(self, resolution=20.0):
        self.resolution = float(resolution)
        self.tick_delay = 1000.0 / resolution
        self.now = pygame.time.get_ticks()
        self.prev_tick = self.now
        self.prev_realtick = self.now
        self.next_realtick = self.now + self.tick_delay
        self.delta = 0.0
        self.tick_delta = 0.0
        self.realtick_delta = 0.0
        self.realtick = False


    def tick(self):
	"""this method should be called once per frame"""
        self.realtick = False
        now = self.now = pygame.time.get_ticks()
        if self.now > self.next_realtick:
            self.realtick_delta = (now - self.prev_realtick) / 1000.0
            self.prev_realtick = now
            self.next_realtick += self.tick_delay
            self.realtick = True
        self.delta = (now - self.prev_realtick) / 1000.0
        self.tick_delta = (now - self.prev_tick) / 1000.0
        self.prev_tick = now


class Reactor(object):
    """Manager class for ticking the tickers
    
    A simple collection that is used to call the tick-method of all
    registered objects.
    """
    
    def __init__(self):
        self.tickers = Set()
        self._remove = Set()
        self._add = Set()
        self.iterating = False


    if ITERATE_REACTOR_COPY:
        def tick(self):
            for t in self.tickers.copy():
                t.tick()

        def add(self, ticker):
                self.tickers.add(ticker)

        def remove(self, ticker):
                self.tickers.discard(ticker)

        def clear(self):
                self.tickers.clear()
    else:
        def tick(self):
            self.iterating = True
            for t in self.tickers:
                t.tick()
            self.iterating = False
            if self._add:
                self.tickers |= self._add
                self._add.clear()
            if self._remove:
                self.tickers -= self._remove
                self._remove.clear()

        def add(self, ticker):
            if self.iterating:
                self._add.add(ticker)
            else:
                self.tickers.add(ticker)

        def remove(self, ticker):
            if self.iterating:
                self._remove.add(ticker)
            else:
                self.tickers.discard(ticker)

        def clear(self):
            if self.iterating:
                self._remove = Set(self.tickers)
            else:
                self.tickers.clear()
        
