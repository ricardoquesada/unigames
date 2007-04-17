"""A convenience module for importing all essential pygext.gl symbols.

The purpose of this module is to import all pygext.gl symbols so that
users of this framework don't have to learn the deep package structure.
Pretty much all names that are supposed to be accessed directly can be
found in this module (the sub-modules are designed with this in mind,
so there will be no internal naming conflicts).

You can safely do: from pygext.gl.all import *
or if you don't want a huge amount of names to your global
namespace: import pygext.gl.all as pgl.
"""

from pygext.gl import *
from pygext.gl import gui
from pygext.gl.gui.simple import *
from pygext.gl.font import *
from pygext.gl.shapes import *
from pygext.gl.resources import *
from pygext.gl.particles import *
#from pygext.gl.vector.primitives import *
from pygext.gl.vector.base import InheritColor
from pygext.gl.director import *
from pygext.gl.director.scene import *
from pygext.gl.director.node import Node
from pygext.gl.director.entities import *
from pygext.gl.director.proxy import *
from pygext.gl.director.emitter import *
from pygext.gl.director.animation import *
from pygext.gl.director.reactor import *
from pygext.gl.director.actions import *
from pygext.gl.director.globals import director
from pygext.gl.director.collision import *
from pygext.gl.mouse import glmouse

from pygext.debug import debugmode

