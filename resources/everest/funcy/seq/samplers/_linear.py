from itertools import chain

from ...constructor import Fn
from ..algorithmic import _Algorithmic

class Bifurcate(_Algorithmic):
    __slots__ = ('_length', '_stop')
    _algorithm = Fn[1 : 2 ** (Fn.n + 1) : 2] / 2 ** (Fn.n + 1)
    def __init__(self, lBnd, uBnd, **kwargs):
        super().__init__(lBnd, uBnd, **kwargs)
    def _iter(self):
        lBnd, uBnd = self._resolve_terms()
        yield lBnd
        yield uBnd
        valRange = uBnd - lBnd
        for v in chain.from_iterable(super()._iter()):
            yield v * valRange + lBnd
