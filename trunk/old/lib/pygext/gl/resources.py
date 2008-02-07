"""pygext.gl.resources - Global resource management

This module contains a global "resources" object that is
used to load and cache resouces such as images and sounds.
This way, you can just specify the filename of e.g. entity
images, and the image will be loaded automatically (or taken
from cache).
"""

import os, sys
import pygame
from pygext.gl.shapes.bitmap import Bitmap

__all__ = [
    "resources",
    ]

class ResourceHandler(object):
    """Global cache for resources"""
    
    def __init__(self):
        self.bitmaps = {}
        self.anims = {}

    def has_bitmap(self, path):
        return path in self.bitmaps

    def init_bitmap(self, path, surface):
        """Initialize a bitmap cache from a Pygame surface
        """
        bmp = Bitmap(surface)
        self.bitmaps[path] = bmp
        return bmp

    def get_bitmap(self, path, hotspot=None):
	"""Load a new Bitmap object from an image file.
	
	Loads an image file from given path and intializes it as
	a pygext.gl.shapes.Bitmap object. If the image has already
	loaded, the same Bitmap object is returned from cache.
	
	@return the loaded Bitmap
	"""
        try:
            bmp = self.bitmaps[path]
        except KeyError:
            bmp = Bitmap(path)
            self.bitmaps[path] = bmp
        if hotspot is not None and bmp.hotspot != hotspot:
            bmp = bmp.copy()
            bmp.set_hotspot(*hotspot)
            self.bitmaps[path] = bmp
        return bmp

    def has_anim(self, path):
        return path in self.anims

    def init_anim(self, path, frames):
        fs = []
        for f in frames:
            if type(f) is pygame.Surface:
                fs.append(Bitmap(f))
            else:
                fs.append(f)
        self.anims[path] = fs
        return fs

    def get_anim(self, path, hotspot=None):
	"""Load an image sequence as an animation.
	
	This method loads an animation that is split into several files
	so that each animation frame is stored in a separate file. The
	path should be in the format "myanim%i.png". In this case the
	method will look for files named myanim0.png, myanim1.png etc.
	and load them as a list of Bitmap objects.
	
	@return list of loaded Bitmaps
	"""
        try:
            return self.anims[path]
        except KeyError:
            frames = [self.get_bitmap(x,hotspot)
                      for x in self._find_anim_frames(path)]
            if not frames:
                raise IOError, "no files found using the %r pattern" % path
            self.anims[path] = frames
            return frames

    def _find_anim_frames(self, path):
        found = False
##        if not os.path.isabs(path):
##            path = os.path.join(sys.path[0], path)
        for i in range(150):
            fn = path % i
            if os.path.exists(fn):
                yield fn
                found = True
            elif found:
                return
        

resources = ResourceHandler()
