"""Light halo effect
"""

import pygame
from pygame.locals import *
import Numeric as N

__all__ = [
    "halocircle",
    ]

def halocircle(color, coreradius, haloradius, corealpha=1.0, haloalphamax=1.0, haloalphamin=1.0):
    """halocircle(color, coreradius, haloradius, corealpha=1.0, haloalphamax=1.0, haloalphamin=1.0) -> Surface
    
    Generate a filled circle with a "halo", i.e. alpha blended border. Useful
    for e.g. particle effects.
    """
    import Numeric as N
    radius = coreradius + haloradius
    r2 = radius*2+2
    x,y = N.indices((r2,r2))
    x -= radius
    y -= radius
    rng = N.sqrt(x*x + y*y)    
    haloalpha = (radius-rng)/float(haloradius)*(haloalphamax-haloalphamin)+haloalphamin    
    alpha = N.where(rng <= coreradius+haloradius, haloalpha, 0)
    alpha = N.where(rng <= coreradius, corealpha, alpha)
    #alpha = N.where(alpha < 0, 0, alpha)
    #alpha = N.where(alpha > 1, 1, alpha)
    surf = pygame.Surface((r2,r2), SRCALPHA, 32)
    if len(color) == 3:
        color += (255,)        
    surf.fill(color)
    pixels = pygame.surfarray.pixels_alpha(surf)
    pixels[...] = (alpha*255).astype(N.UnsignedInt8)
    return surf
