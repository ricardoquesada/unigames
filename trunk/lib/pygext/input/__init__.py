"""Miscellanous input handling

XXX: work in progress
"""

import pygame
from pygame.locals import *

def wait_anykey():
    old = pygame.event.get_allowed()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([KEYDOWN])
    pygame.event.wait()    
    pygame.event.set_allowed(None)
    pygame.event.set_allowed(old)
