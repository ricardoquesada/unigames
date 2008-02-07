"""Utilities for lazy evaluation"""

from random import random, randrange

__all__ = [
    "Lazy",
    "Random",
    "RandRange",
    ]

def _c(val):
    if isistance(val, Lazy):
        return val.func()
    return val

class Lazy(object):
    def __init__(self, func):
        self.func = func

    def __float__(self):
        return float(self.func())

    def __int__(self):
        return int(self.func())

    def __add__(self, val):
        return Lazy(lambda: self.func() + _c(val))

    def __sub__(self, val):
        return Lazy(lambda: self.func() - _c(val))

    def __mul__(self, val):
        return Lazy(lambda: self.func() * _c(val))

    def __div__(self, val):
        return Lazy(lambda: self.func() / _c(val))

    def __radd__(self, val):
        return Lazy(lambda: _c(val) + self.func())

    def __rsub__(self, val):
        return Lazy(lambda: _c(val) - self.func())

    def __rmul__(self, val):
        return Lazy(lambda: _c(val) * self.func())

    def __rdiv__(self, val):
        return Lazy(lambda: _c(val) / self.func())

    def __neg__(self):
        return Lazy(lambda: -self.func())

class Random(Lazy):
    def __init__(self, low, high=None):
        if high is None:
            high = low
            low = 0
        self.low = low
        self.high = high
        Lazy.__init__(self, self._val)

    def _val(self):
        return random()*(self.high-self.low)+self.low

class RandRange(Random):

    def _val(self):
        return randrange(self.low, self.high)

