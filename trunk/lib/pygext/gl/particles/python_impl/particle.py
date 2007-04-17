
__all__ = [
    "Particle",
    ]

try:
    from psyco.classes import *
except:
    pass


class Particle(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.color = (1.0,1.0,1.0,1.0)
        self.scale = 1.0
        self.scaled = 0.0
        self.rotation = 0
        self.rotationd = 0
        self.life = 0
        self.age = 0
        self.fade_time = 0
        self.fade_in = 0
        self.collnode = None
