"""RGBA value utilities
"""

def _conv_color(r,g,b,a=255):
    r /= 255.0
    g /= 255.0
    b /= 255.0
    a /= 255.0
    return r,g,b,a

def _blend(color1, color2, x):
    r = x
    l = 1-x
    lr,lg,lb,la = color1
    rr,rg,rb,ra = color2

    cr = l*lr + r*rr
    cg = l*lg + r*rg
    cb = l*lb + r*rb
    ca = l*la + r*ra
    return (cr,cg,cb,ca)

class Gradient(object):
    def get_color(self, x, y, bounds):
        """implement this in subclasses"""

class HGradient(Gradient):
    """horizontal gradient"""
    def __init__(self, left_color, right_color):
        self.left_color = _conv_color(*left_color)
        self.right_color = _conv_color(*right_color)
    
    def get_color(self, x, y, bounds):
        xmin = bounds[0]
        xmax = bounds[1]
        r = (x-xmin)/float(xmax-xmin)
        return _blend(self.left_color, self.right_color, r)

class VGradient(Gradient):
    def __init__(self, top_color, bottom_color):
        self.top_color = _conv_color(*top_color)
        self.bottom_color = _conv_color(*bottom_color)
    
    def get_color(self, x, y, bounds):
        ymin = bounds[2]
        ymax = bounds[3]
        r = (y-ymin)/float(ymax-ymin)
        return _blend(self.top_color, self.bottom_color, r)
