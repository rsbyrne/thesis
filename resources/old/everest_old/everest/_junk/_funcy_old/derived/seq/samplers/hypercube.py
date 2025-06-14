###############################################################################
''''''
###############################################################################

import numpy as np
from diversipy.hycusampling import improved_lhd_matrix

from . import _Seq
from . import _reseed

class HyperCube(_Seq):
    pass

class Latin(HyperCube):
    def __init__(self, lower, upper, n, seed = None):
        if not len(lower) == len(upper):
            raise ValueError
        super().__init__(lower, upper, n, seed)
        self.samples = latin_hypercube(n, len(lower), lower, upper, seed = seed)
    def _iter(self):
        return (list(row) for row in self.samples)
    def _seqLength(self):
        return len(self.samples)

@_reseed.reseed
def latin_hypercube(n, d, lower = 0, upper = 1):
    lower, upper = (
        np.full(d, bnd) if not isinstance(bnd, np.ndarray)
            else bnd for bnd in (lower, upper)
        )
    samples = improved_lhd_matrix(n, d)
    return samples / n * (upper - lower) + lower

# class Bifurcate(HyperCube):
#     def __init__(self, lower, upper, n)

###############################################################################
''''''
###############################################################################
