"""Vector algebra
"""

import Numeric as N
import math

__all__ = [
    "vec",
    "veclen",
    "unitvec",
    "ortho",
    "orthounit",
    "midnormal",
    "angle",
    "direction",
    "sincos",
    ]

def sincos(angle, magnitude):
    angle = math.pi + math.pi * angle/180.0
    x = -math.sin(angle) * magnitude
    y = math.cos(angle) * magnitude
    return x,y

def vec(x,y):
    """vec(x,y) -> numarray
    
    Wrap coordinates to a Numeric array
    """
    return N.array([x,y])

def veclen(A):
    """veclen(A) -> float
    
    Length of a vector.
    """
    l = math.sqrt(N.sum(A**2))
    return l

def unitvec(A):
    """univec(A) -> B
    
    Unit vector with the same direction as A
    """
    return A/veclen(A)

def ortho(A):
    """ortho(A) -> B
    
    New vector that is orthogonal to A
    """
    x,y = A
    return vec(y,-x)

def orthounit(A):
    """orthounit(A) -> B
    
    New unit vector that is orthogonal to A
    """
    return ortho(A)/veclen(A)

def midnormal(A,B):
    """midnormal(A,B) - > C
    
    A unit vector in the midpoint angle between A and B.
    
    I.e.
    
    A  C  B
     \ | /
      \|/
    """
    D = A+B
    return D/veclen(D)

def direction(V):
    """direction(V) -> angle
    
    The direction in degrees where the vector is pointing.
    0 degrees is up.
    """
    #B = unitvec(B-A)
    B = unitvec(vec(*V))
    A = [0,-1]
    dot = N.dot(A,B)
    a = -math.acos(dot) / math.pi * 180.0
    if B[0] > 0:
        a = 360 - a
    return a
    
def angle(A,B):
    """angle(A,B) -> angle
    
    The angle between A and B
    """
    return direction(B)-direction(A)
