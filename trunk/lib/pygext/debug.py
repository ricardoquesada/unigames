"""Debugging utilities
"""

import sys, gc #, Polygon

#print Polygon.version
#print Polygon.withNumeric

__all__ = [
    "debugmode",
    "print_obj_stats",
    ]

class DebugMode(object):
    """Small utility object for keeping track of the debug flag.
    
    This wrapper class is used, so you can import "debugmode"
    to your global namespace and mutate it, instead of referring
    to debug.debugmode.
    """
    def __init__(self):
        self.active = False

    def set(self, flag):
        self.active = flag

    def __nonzero__(self):
        return self.active

debugmode = DebugMode()

if "--debug" in sys.argv:
    debugmode.set(True)

def print_obj_stats():
    """Print information about current live objects
    """
    count = {}
    objects = gc.get_objects()
    print "Live objects:", len(objects)

    for obj in objects:
        t = str(type(obj))
        count[t] = count.get(t,0) + 1
    items = count.items()
    items.sort()
    for name,count in items:
        print "% -30s %s" % (name,count)
