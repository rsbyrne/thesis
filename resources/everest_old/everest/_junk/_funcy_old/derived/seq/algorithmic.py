###############################################################################
''''''
###############################################################################

from functools import cached_property as _cached_property

from . import _special
from .seq import Seq as _Seq

class _Algorithmic(_Seq):
    _algorithm = None
    @_cached_property
    def n(self):
        return self.Fn(0, name = 'n')
    @_cached_property
    def algorithm(self):
        return self._algorithm.close(_seq_n = self.n)
    def _iter(self):
        self.n.value = -1
        while True:
            self.n += 1
            yield self.algorithm.value
    def _seqLength(self):
        return _special.inf

class Algorithmic(_Algorithmic):
    def __init__(self, algorithm):
        self._algorithm = algorithm
        super().__init__(self.algorithm)

###############################################################################
''''''
###############################################################################
