
__all__ = [
    "ParticleMutator",
    "LinearForce",
    ]

try:
    from psyco.classes import *
except:
    pass

class ParticleMutator(object):
    def mutate(self, particles, delta):
        pass


class LinearForce(ParticleMutator):

    def __init__(self, fx, fy):
        self.force = (fx,fy)

    def mutate(self, particles, delta):
        fx,fy = self.force
        for p in particles:
            p.vx += fx * delta
            p.vy += fy * delta
