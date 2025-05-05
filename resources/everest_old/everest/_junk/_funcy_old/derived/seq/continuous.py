###############################################################################
''''''
###############################################################################

from . import _reseed, _special
from . import _special
from .seq import Seeded as _Seeded, Seq as _Seq

def process_scalar(scal):
    return scal.dtype.type(scal)

class _Continuous(_Seq):
    def _seqLength(self):
        return _special.inf

class Continuum(_Continuous, _Seeded):
    def __init__(self, start = 0., stop = 1., step = None, **kwargs):
        start = 0. if start is None else start
        stop = 1. if stop is None else stop
        super().__init__(start, stop, step, **kwargs)
    def _iter(self):
        start, stop, _ = self._resolve_terms()
        seed = self._startseed
        while True:
            v = _reseed.rangearr(start, stop, seed = seed)
            if not len(v.shape):
                v = process_scalar(v)
            yield v
            seed += 1
    def _seqLength(self):
        return _special.inf

###############################################################################
''''''
###############################################################################
