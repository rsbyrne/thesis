from everest import reseed

from ..utilities import process_scalar
from ..special import *
from .base import Seeded, Seq
from .base import Seq

class Continuous(Seq):
    def _seqLength(self):
        return inf

class Continuum(Continuous, Seeded):
    def __init__(self, start = 0., stop = 1., step = None, **kwargs):
        start = 0. if start is None else start
        stop = 1. if stop is None else stop
        super().__init__(start, stop, step, **kwargs)
    def _iter(self):
        start, stop, _ = self._resolve_terms()
        seed = self._startseed
        while True:
            v = reseed.rangearr(start, stop, seed = seed)
            if not len(v.shape):
                v = process_scalar(v)
            yield v
            seed += 1
    def _seqLength(self):
        return inf
