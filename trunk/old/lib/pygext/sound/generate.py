"""Sound FX generation

XXX: work in progress

This library is mainly useful for generating low-frequency
"retro" sound effects.
"""

import Numeric as N
import pygame
import random

__all__ = [
    "make",
    "sinewave",
    "linear",
    "concat",
    "add_sin",
    "add_cos",
    "add_noise",
    "add_fadein",
    "add_fadeout",
    ]

## XXX TODO: remove hard coded mixer values
pygame.mixer.init(11025, -16, 1)

def make(a):
    """make(array) -> Sound
    
    Convert an array into a pygame Sound object
    """
    return pygame.sndarray.make_sound(a)

def sinewave(size, freq, amplitude):
    """sinewave(size, frequency, amplitude) -> array
    
    Create a new sine array.
    """
    freq *= 0.001
    a = N.array(xrange(size)) * freq
    return (N.sin(a) * amplitude).astype(N.Int0)

def linear(size, begin_freq, end_freq, amplitude):
    """linear(size, begin_frequency, end_frequency, amplitude) -> array
    
    Create a new sine array where the frequency changes linerily.
    """
    begin_freq *= 0.001
    end_freq *= 0.001
    a = N.array(xrange(size), N.Float)
    freq = N.array(xrange(size)) * (end_freq - begin_freq) / float(size) + begin_freq
    a *= freq
    return (N.sin(a) * amplitude).astype(N.Int0)

def concat(a,b):
    """concat(array1, array2) -> array
    
    Concatenate two arrays
    """
    c = N.zeros(len(a)+len(b), N.Int0)
    c[:len(a)] = a
    c[len(a):] = b
    return c

def add_sin(a, freq, amplitude):
    """add_sin(array, frequency, amplitude)
    
    Add a sine wave to the given array
    """
    freq *= 0.001
    b = N.array(xrange(len(a))) * freq
    b = (N.sin(b) * amplitude).astype(N.Int0)
    a += b
    return a
    
def add_cos(a, freq, amplitude):
    """add_cos(array, frequency, amplitude)
    
    Add a cosine wave to the given array.
    """
    freq *= 0.001
    b = N.array(xrange(len(a))) * freq
    b = (N.cos(b) * amplitude).astype(N.Int0)
    a += b
    return a

def add_noise(a, intensity):
    """add_noise(array, intensity)
    
    Add random noise to the given array.
    """
    import RandomArray
    b = RandomArray.randint(-intensity, intensity+1, a.shape).astype(N.Int0)
    a += b
    return a

def add_fadein(a, length):
    """add_fadein(array, length)
    
    Fade the volume of the wave from 0% to 100% during the given length.
    """
    b = N.ones(len(a), N.Float)
    b[:length] *= N.array(xrange(length), N.Float) / length
    b *= a
    a[:] = b.astype(N.Int0)
    return a
    
def add_fadeout(a, length):
    """add_fadeout(array, length)
    
    Fade out the volume of the array from %100 to %0 during the given length.
    """
    b = N.ones(len(a), N.Float)
    b[-length:] *= N.array(xrange(length-1,-1,-1), N.Float) / length
    b *= a
    a[:] = b.astype(N.Int0)
    return a
