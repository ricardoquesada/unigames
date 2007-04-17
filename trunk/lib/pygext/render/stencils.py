"""Image stencils
"""

import pygame
from pygame.locals import *
import Numeric as N

__all__ = [
    'alpha_stencil',
    'raster',
    ]

def alpha_stencil(image):
    """alpha_stencil(surface) -> Surface
    
    Return a copy of the surface that retains its original alpha values,
    but the color of all pixels is reset to white.
    """
    s = pygame.Surface(image.get_size(), SRCALPHA, 32)
    s.fill((255,255,255,255))
    a = pygame.surfarray.pixels_alpha(s)
    a[...] = pygame.surfarray.pixels_alpha(image)
    return s

def raster(size, color1, color2): ## XXX TODO: move to rects.py
    s = pygame.Surface(size, 0, 32)
    s.fill(color1)
    x,y = size
    color1 = s.map_rgb(color1)
    color2 = s.map_rgb(color2)
    a = pygame.surfarray.pixels2d(s)
    a[1::2,::2] = color2
    a[::2,1::2] = color2
    return s
