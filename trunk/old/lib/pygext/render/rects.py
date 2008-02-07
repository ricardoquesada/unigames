"""Rectangles
"""

import pygame
from pygame.locals import *

__all__ = [
    'rect3d',
    'rounded_rect',
    'rounded_hollow_rect',
    ]

def rect3d(size, border, color, hi_color, low_color):
    """rect3d(size, border, color, hi_color, low_color) -> Surface
    
    Generate a shaded, button-like rect. 
    """
    s = pygame.Surface(size, 0, 32)
    x,y = size
    pygame.draw.polygon(s, hi_color, [(0,0),(x,0),(x,y)])
    pygame.draw.polygon(s, low_color, [(0,0), (0,y), (x,y)])
    r = Rect(0,0,x,y)
    r.inflate_ip((-border,-border))
    s.fill(color, r)
    return s

def _draw_rrect(surface, color, rect, corner_radius):
    oldclip = surface.get_clip()
    newclip = oldclip.clip(rect)
    surface.set_clip(newclip)
    rect = Rect(rect)    
    r = rect.inflate(-corner_radius*2, -corner_radius*2)
    for pos in (r.topleft, r.topright, r.bottomleft, r.bottomright):
        pygame.draw.circle(surface, color, pos, corner_radius, 0)
    pygame.draw.rect(surface, color, rect.inflate(-corner_radius*2,0), 0)
    pygame.draw.rect(surface, color, rect.inflate(0,-corner_radius*2), 0)
    surface.set_clip(oldclip)

def rounded_rect(color, size, corner_radius):
    """rounded_rect(color, size, corner_radius) -> Surface
    
    Generate a rectangle with round borders.
    """
    rect = Rect(0,0,size[0],size[1])
    s = pygame.Surface(size)
    s.fill((0,0,0))
    _draw_rrect(s, color, rect, corner_radius)
    s.set_colorkey((0,0,0))
    return s

def rounded_hollow_rect(color, size, corner_radius, border):
    xs,ys = size
    rect = Rect(0,0,xs,ys)
    inner = Rect(border,border,xs-border*2,ys-border*2)
    s = pygame.Surface(size, SRCALPHA, 32)
    s.fill((0,0,0,0))
    _draw_rrect(s, color, rect, corner_radius)
    _draw_rrect(s, (0,0,0,0), inner, corner_radius)
    return s.convert_alpha()
    
