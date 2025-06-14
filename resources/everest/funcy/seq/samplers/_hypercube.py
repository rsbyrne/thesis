from ..base import Seq

class HyperCube(Seq):
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

import numpy as np
from everest import reseed

@reseed.reseed
def latin_hypercube(n, d, lower = 0, upper = 1):
    from diversipy.hycusampling import improved_lhd_matrix
    lower, upper = (
        np.full(d, bnd) if not isinstance(bnd, np.ndarray)
            else bnd for bnd in (lower, upper)
        )
    samples = improved_lhd_matrix(n, d)
    return samples / n * (upper - lower) + lower

# class Bifurcate(HyperCube):
#     def __init__(self, lower, upper, n)
