import numpy as np

from everest.flavours import Particles

class Lorenz(Particles):

    def __init__(self,
            # params
                s = 10,
                r = 28,
                b = 2.667,
                dt = 0.01,
            # _configs
                coords = [0., 1., 1.05],
            **kwargs
            ):

        super().__init__(**kwargs)

        x, y, z = (self.state['coords'][i:i+1] for i in range(3))
        self.coords = self.state['coords']
        self.chron = self.indices['chron']
        def integrate():
            self.coords[...] = (
                x + dt * (s * (y - x)),
                y + dt * (r * x - y - x * z),
                z + dt * (x * y - b * z),
                )
            self.chron += dt
        self.integrate = integrate

    def _iterate(self):
        self.integrate()

# def integrate(cs, chron):
#     cs += (
#         dt * (s * (cs[1] - cs[0])),
#         dt * (r * cs[0] - cs[1] - cs[0] * cs[2]),
#         dt * (cs[0] * cs[1] - b * cs[2]),
#         )
#     chron += dt
