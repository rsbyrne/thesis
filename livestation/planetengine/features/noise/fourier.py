import random
import math

from underworld import function as fn
from planetengine.utilities import get_prioritySubstrate
from . import Noise

class Fourier(Noise):

    species = 'fourier'

    def __init__(
            self,
            pert = 1e-6,
            freq = 1e6,
            iterations = 6,
            seed = 1066,
            ):

        randTerms = []
        coordFns = fn.coord()
        x, y = coordFns[0], coordFns[1]
        radii = (fn.misc.constant(0.), fn.misc.constant(1.))
        radFn = (fn.math.sqrt(x**2 + y**2) - radii[0]) \
            / (radii[1] - radii[0])
        angFn = fn.math.atan2(y, x)
        for i in range(iterations):
            randPhase = fn.misc.constant(1.)
            phase = randPhase * math.pi
            partFn = pert * fn.math.sin(freq * (angFn + phase))
            randTerms.extend([randPhase,])
            freq *= 2.
            pert /= 2.
            if i == 0: combFn = partFn
            else: combFn += partFn
        depthEaser = fn.math.sin(math.pi * radFn)
        waveFn = fn.misc.constant(1.) + depthEaser * combFn
        self.seed = seed
        self.radii = radii
        self.waveFn = waveFn
        self.randTerms = randTerms
        self._preditherings = dict()
        self._system = None

        super().__init__()

    def _attach(self, system):
        radialLengths = system.locals.mesh.radialLengths
        self.radii[0].value, self.radii[1].value = radialLengths

    def randomise(self, seed = 0):
        random.seed((self.seed, *seed))
        for randTerm in self.randTerms:
            randTerm.value = random.random()
        random.seed()

    def apply(self, var, seed):
        self.randomise(seed)
        substrate = get_prioritySubstrate(var)
        dithering = self.waveFn.evaluate(substrate)
        var.data[:] *= dithering

CLASS = Fourier
