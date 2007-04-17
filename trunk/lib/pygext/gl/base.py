##"""Base functionality
##"""
##
##__all__ = [
##    'init',    
##    'clear_screen',
##    'flip_screen',
##    ]
##
##import pygame
##from pygame.locals import *
##from OpenGL.GL import *
##import sys
##
##def init(resolution, screenunits=None, fullscreen=False, title="Pygext Game"):
##    """Init the vector graphics engine and pygame display.
##    
##      resolution  - the actual screen resolution in pixels eg. (640,480)
##      screenunits - screen size in "units" used for vector drawing (default is the same as resolution)
##      fullscreen  - fullscreen flag (default is False)
##      title       - window title
##
##    If the unit size is the same as the resolution, one unit will
##    equal one pixel.
##    """
##    if screenunits is None:
##        screenunits = resolution
##    _init_display(resolution[0], resolution[1], fullscreen=fullscreen)
##    pygame.display.set_caption(title)
##    pygame.mouse.set_visible(False)
##    _init_gl(*screenunits)
##
##def clear_screen():
##    """Clear the hidden buffer in double buffered mode.
##    """
##    glClear(GL_COLOR_BUFFER_BIT)
##    glMatrixMode(GL_MODELVIEW)
##    glLoadIdentity()    
##
##def flip_screen():
##    """Flip the visible buffer in double buffered mode.
##    """
##    #glFlush()
##    pygame.display.flip()
##
##def _init_display(xsize, ysize, fullscreen=False):
##    resolution = (xsize,ysize)
##    pygame.init()
##    flags = OPENGL|DOUBLEBUF|HWSURFACE
##    if fullscreen:
##        flags |= FULLSCREEN
##    pygame.display.set_mode(resolution, flags)
##
##def _init_gl(xunits, yunits):
##    glClearColor(0,0,0,0)
##    glMatrixMode(GL_PROJECTION)
##    glLoadIdentity()
##    glOrtho(0,xunits,yunits,0,-1,1)
##    glMatrixMode(GL_MODELVIEW)
##    glLoadIdentity()
##    glDisable(GL_DEPTH_TEST)
##    glEnable(GL_BLEND)
##    glEnable(GL_TEXTURE_2D)
##    glShadeModel(GL_SMOOTH)
##    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
##    glColor4f(1,1,1,1)
