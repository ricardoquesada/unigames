"""Utilities for generating graphics programmatically with surfarray
"""

import pygame
from pygame.locals import *
import Numeric as N
from random import random

__all__ = [
    "colorize",
    "copy_alpha",
    "xy_arrays",
    "dist_array",
    "scale_to_01",
    "color_array",
    "cut_array",
    "make_rgba",
    "make_stencil",
    "double",
    "soft_enlarge",
    "color_slide",
    "fractalize",
    ]

def colorize(surface, r,g,b):
    a = pygame.surfarray.array3d(surface)
    mult = a[..., 0] / 255.0
    t = a.typecode()
    reds = (r * mult).astype(t)
    greens = (g * mult).astype(t)
    blues = (b * mult).astype(t)
    s = pygame.Surface(surface.get_size(), SRCALPHA, 32)
    a = pygame.surfarray.pixels3d(s)
    a[...,0] = reds
    a[...,1] = greens
    a[...,2] = blues
    copy_alpha(surface, s)
    return s


def xy_arrays(xsize, ysize):
    """Returns xarray and yarray that have the specified shape.

    E.g. xy_arrays(3,4) will return the arrays

    [[0,0,0,0]   [[0,1,2,3]
     [1,1,1,1]    [0,1,2,3]
     [2,2,2,2]]   [0,1,2,3]]
    """
    return N.indices((xsize, ysize))

def dist_array(xsize, ysize):
    """Returns a float array where each element is the distance to the
    center of the array.
    """

    x,y = xy_arrays(xsize, ysize)
    cx = xsize / 2.0
    cy = ysize / 2.0
    dx = x - cx
    dy = y - cy
    dist = N.sqrt(dx*dx+dy*dy)
    return dist

def scale_to_01(array):
    """Return a version of the array where all values are scaled to the range [0,1]
    """
    m = max(N.ravel(array))
    return array / float(m)

def color_array(xsize, ysize, r,g,b,a=255, values=4):
    return N.resize((r,g,b,a), (xsize, ysize, values))

def make_rgba(array, values=4):
    """Resize an (xsize,ysize) array into (xsize,ysize,values)
    """
    xsize, ysize = array.shape
    tmp = N.ravel(array)
    tmp = N.repeat(tmp, values)
    tmp = N.resize(tmp, (xsize, ysize, values))
    print tmp.shape
    return tmp

def cut_array(array, minvalue=None, maxvalue=None):
    """Cut off values so that all elements < minvalue become minvalue
    and all elements > maxvalue become maxvalue.
    """
    if minvalue is not None:
        array = N.where(array < minvalue, minvalue, array)
    if maxvalue is not None:
        array = N.where(array > maxvalue, maxvalue, array)
    return array

def make_surface(array):
    xsize,ysize,rgba = array.shape
    rgb = array[...,:3].astype(N.Int0)
    s = pygame.surfarray.make_surface(rgb)
    if rgba == 4:
        a = pygame.surfarray.pixels_alpha(s)
        a[...] = array[...,3]
        del a
    return s
    
def make_stencil(alpha_array, r=255, g=255, b=255):
    if type(r) is tuple:
        r,g,b = r
    xsize, ysize = alpha_array.shape
    s = pygame.Surface((xsize,ysize), SRCALPHA ,32)
    s.fill((r,g,b,255))
    a = alpha_array.astype(N.UnsignedInt8)
    aa = pygame.surfarray.pixels_alpha(s)
    aa[...] = a
    del aa
    return s

def copy_alpha(src, dst):
    pygame.surfarray.pixels_alpha(dst)[...] = pygame.surfarray.array_alpha(src)

def double(array):
    """Resize an (xsize,ysize,...) array into (xsize*2, ysize*2, ...)
    """
    return N.repeat(N.repeat(array, 2,axis=0), 2, axis=1)

def soft_enlarge(array):
    """Resize an (xsize, ysize) array to (xsize*2-1, ysize*2-1) so that
    all intermediate values are interpolated.
    """
    a = array
    x,y = a.shape
    b = N.zeros((x*2-1,y*2-1),N.Float64)
    b[::2,::2] = a
    aa = a[:,:-1]
    ab = a[:,1:]
    ac = a[:-1,:]
    ad = a[1:,:]
    aaa = a[:-1,:-1]
    aab = a[1:,1:]
    aac = a[:-1,1:]
    aad = a[1:,:-1]
    b[::2, 1::2] += aa
    b[::2, 1::2] += ab
    b[1::2,::2] += ac
    b[1::2,::2] += ad
    b[1::2,1::2] += aaa
    b[1::2,1::2] += aab
    b[1::2,1::2] += aac
    b[1::2,1::2] += aad
    b[::,1::2] /= 2.0
    b[1::2,::] /= 2.0
    return b

def color_slide(array, color1, color2):
    """Return an (r,g,b,a) array where 0.0 = color1 and 1.0 = color2 and interpolated values inbetween.

    Values less than 0.0 will all be color1 and values over 1.0 will all be color2.
    """
    array = N.clip(array, 0.0, 1.0)
    inverse = -array + 1.0
    xsize,ysize = array.shape
    a1 = color_array(xsize, ysize, *color1)
    a2 = color_array(xsize, ysize, *color2)

    colorarray = make_rgba(inverse)*a1 + make_rgba(array)*a2
    return colorarray.astype(N.Int0)


def fractalize(a, delta):
    """Enlarge the image like soft_enlarge, but add random variation
    """
    b = _enlarge(a)
    _randomize(b, delta)
    return b

def sym_fractalize(a, delta):
    b = _enlarge(_symmetric(a))
    _randomize(b, delta)
    return b


def _symmetric(a):
    a = array(a)
    a[:,-1] = a[:,0]
    a[-1,:] = a[0,:]
    return a

def _randomize(a, delta):
    x,y = a.shape
    d = delta / (x**1.1)
    d2 = d / 2
    l = [random()*d-d2 for i in range(x*y)]
    b = N.resize(l, (x,y))
    a += b

def _enlarge(array):
    a = array
    x,y = a.shape
    b = N.zeros((x*2-1,y*2-1),N.Float64)
    b[::2,::2] = a
    aa = a[:,:-1]
    ab = a[:,1:]
    ac = a[:-1,:]
    ad = a[1:,:]
    aaa = a[:-1,:-1]
    aab = a[1:,1:]
    aac = a[:-1,1:]
    aad = a[1:,:-1]
    b[::2, 1::2] += aa
    b[::2, 1::2] += ab
    b[1::2,::2] += ac
    b[1::2,::2] += ad
    b[1::2,1::2] += aaa
    b[1::2,1::2] += aab
    b[1::2,1::2] += aac
    b[1::2,1::2] += aad
    b[::,1::2] /= 2.0
    b[1::2,::] /= 2.0
    return b


def _test():
    import pygame
    import pygame.locals as l
    pygame.display.init()
    screen = pygame.display.set_mode((800,600), 0, 32)
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([l.KEYDOWN])
    img = pygame.image.load("test.png")    
    a = pygame.surfarray.array3d(img)[...,1]
    b = pygame.surfarray.array3d(img)[...,0]
    for x in range(5):
        screen.fill((0,0,0))
        a = fractalize(a, 10000*(x+1))
        b = fractalize(b, 10000*(x+1))
        rgb = color_array(*(a.shape + (0,0,0)), **{'values':3})
        rgb[...,0] = N.clip(b,0,255).astype(N.Int0)
        rgb[...,1] = N.clip(a,0,255).astype(N.Int0)
        print rgb.shape
        s = pygame.surfarray.make_surface(rgb.astype(N.Int0))
        screen.blit(s, (50,50))
        pygame.display.update()
        pygame.event.wait()


if __name__ == '__main__':
    _test()
