##
## pyVectorGFX - primitive shapes
##
## author: Sami Hangaslammi
## email:  shang@iki.fi
##

from pygext.gl.vector.base import Primitive, glprimitive
from pygext.math.vecalg import *
import math

try:
    from Polygon import Polygon
except ImportError:
    Polygon = None


__all__ = (
    "line","multiline",
    "rect", "recth",
    "circle", "circleh",
    "sector", "sectorh",
    "poly", "polyh",
    "polycut", "polyfit", "polyjoin", "polysplit"
    )

def line(x,y,xx,yy,width=1):
    A = vec(x,y)
    B = vec(xx,yy)
    O = orthounit(B-A) * width * 0.5
    pts = [A-O,A+O,B+O,B-O]
    return Polygon(pts)
line = glprimitive(line)

def multiline(pts, width=1):
    ap = []
    bp = []
    a = ap.append
    b = bp.append
    A = vec(*pts[0])
    B = vec(*pts[1])
    O = orthounit(B-A) * width * 0.5
    a(A-O)
    b(A+O)
    for i in range(1, len(pts)-1):
        A = vec(*pts[i])
        AB = vec(*pts[i-1])-A
        AC = vec(*pts[i+1])-A
        O = midnormal(AB,AC) * width * 0.5
        a(A-O)
        b(A+O)
    A = vec(*pts[-2])
    B = vec(*pts[-1])
    O = orthounit(B-A) * width * 0.5
    a(B-O)
    b(B+O)
    bp.reverse()
    return Polygon(ap+bp)
multiline = glprimitive(multiline)

def rect(x, y, xsize=None, ysize=None):
    if xsize is None:        
        xsize = x
        ysize = y
        x = -xsize / 2.0
        y = -ysize / 2.0
    else:
        assert ysize is not None
    return Polygon((
        (x,y),
        (x+xsize,y),
        (x+xsize,y+ysize),
        (x,y+ysize)))
rect = glprimitive(rect)

def recth(x, y, xsize_or_b=None, ysize=None, border=None):
    """hollow rectangle"""
    
    if ysize is None:
        if border is None:
            border = xsize_or_b
        xsize = x
        ysize = y
        x = -xsize / 2.0
        y = -ysize / 2.0
    if border is None:
        border = 1

    p = Polygon((
        (x,y),
        (x+xsize,y),
        (x+xsize,y+ysize),
        (x,y+ysize)
        ))
    p2 = Polygon((
        (x+border,y+border),
        (x+xsize-border,y+border),
        (x+xsize-border,y+ysize-border),
        (x+border,y+ysize-border)
        ))
    return p-p2
recth = glprimitive(recth)

def circle(radius, segments=20):
    full = 2*math.pi
    step = full/float(segments)
    l = []
    for i in range(segments):
        rad = step * i
        x = math.cos(rad) * radius
        y = math.sin(rad) * radius
        l.append((x,y))
    return Polygon(l)
circle = glprimitive(circle)

def circleh(radius, border=None, segments=20):
    if border is None:
        border = 1
    c1 = circle._func(radius,segments)
    c2 = circle._func(radius-border,segments)
    return c1-c2
circleh = glprimitive(circleh)

def _poly(p):
    if type(p) is Primitive:
        return p.transformed_polygon()
    return Polygon(p)

def poly(points):
    return _poly(points)
poly = glprimitive(poly)

def polyh(points, width=1):
    p1 = poly(points)
    p2 = p1.get_interior(width)
    return polycut(p1,p2)

def polycut(points_src, points_cutter):    
    p1 = _poly(points_src)
    p2 = _poly(points_cutter)
    p = Primitive(p1-p2)
    if type(points_src) is Primitive:
        p.mirror_style(points_src)
    return p
    
def polyfit(points_src, points_limit):
    p1 = _poly(points_src)
    p2 = _poly(points_limit)
    p = Primitive(p1 & p2)
    if type(points_src) is Primitive:
        p.mirror_style(points_src)
    return p

def polysplit(points_src, points_splitter):
    p1,p2 = polycut(points_src, points_splitter),\
            polyfit(points_src, points_splitter)
    
    if type(points_src) is Primitive:
        p1.mirror_style(points_src)
        p2.mirror_style(points_src)

    return p1,p2

def polyjoin(poly1, *polys):
    p = _poly(poly1)
    for poly in polys:
        p = p + _poly(poly)
    p = Primitive(p)
    if type(poly1) is Primitive:
        p.mirror_style(poly1)
    return p

def sector(radius, start_deg, end_deg, segments=20):
    full = math.pi * 2
    if end_deg < start_deg:
        end_deg += 360
    start_rad = start_deg/360.0 * full
    end_rad = end_deg/360.0 * full
    step = (end_rad - start_rad) / float(segments)

    l = [(0,0)]
    for i in range(segments):
        rad = i * step + start_rad
        x = math.sin(rad) * radius
        y = -math.cos(rad) * radius
        l.append((x,y))
    return Polygon(l)
sector = glprimitive(sector)

def sectorh(radius, start_deg, end_deg, border=None, segments=20):
    if border is None:
        border = 1
    c1 = sector._func(radius,start_deg,end_deg, segments)
    c2 = circle._func(radius-border,segments)
    return c1-c2
sectorh = glprimitive(sectorh)
