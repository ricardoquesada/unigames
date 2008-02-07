"""Basic shape objects for OpenGL

The GLShapes objects in pygext.gl are used similarily to Surfaces
in Pygame. Shape objects represent all graphics (can be a raster or
vector images). They can be drawn directly to the screen, or assigned
to Entities (see pygext.gl.director.entities).
"""

from pygext.gl.shapes.base import *
from pygext.gl.shapes.composite import Composite
from pygext.gl.shapes.bitmap import Bitmap
from pygext.gl.shapes.pattern import PatternImage
from pygext.gl.shapes.gradient import GradientRect


