###############################################################################
''''''
###############################################################################

from . import _reseed, _special
from .seq import Seeded as _Seeded, Seq as _Seq

from .exceptions import *

class Discrete(_Seq):
    discrete = True
    def _iter(self):
        return (self._value_resolve(v) for v in self.prime)
    def _seqLength(self):
        return len(self.prime)

class Regular(Discrete):
    def __init__(self, start = 0, stop = _special.inf, step = 1, **kwargs):
        if start is None: start = 0
        if stop is None: stop = _special.inf
        if step is None: step = 1
        super().__init__(start, stop, step, **kwargs)
    def _iter(self):
        start, stop, step = self._resolve_terms()
        for i in range(self._seqLength()):
            yield min(start + i * step, stop)
    def _seqLength(self):
        start, stop, step = self._resolve_terms()
        return int((stop - start) / step) + 1

class Shuffle(_Seeded, Discrete):
    def __init__(self, start = 0, stop = 1, seed = None, **kwargs):
        start = 0 if start is None else start
        stop = 1 if stop is None else stop
        super().__init__(start, stop, seed, **kwargs)
    def _seqLength(self):
        return len(self._get_iterItems())
    def _iter(self):
        seed = self._startseed
        items = self._get_iterItems()
        while len(items):
            yield items.pop(
                _reseed.randint(0, len(items) - 1, seed = seed)
                )
            seed += 1
    def _get_iterItems(self):
        start, stop, _ = self._resolve_terms()
        return list(range(start, stop))

class Procedural(Discrete):
    __slots__ = (
        'n',
        'fn',
        'lenFn',
        'stopFn',
        )
    def __init__(self,
            fn, /,
            start = 0, stop = _special.inf, step = 1, **kwargs
            ):
        super().__init__(fn, start, stop, step, **kwargs)
        self.lenFn = start - stop
        self.n = self.Fn(int, name = 'n')
        self.runFn = self.n < nmax
        self.fn = fn.close(n = self.n)
    def _seqLength(self):
        return int(self._value_resolve(self.lenFn))
    def _iter(self):
        n, fn, runFn = self.n, self.fn, self.runFn
        start, stop, step = self.terms[1:]
        self.n.value = start
        while self.runFn:
            self.n += step
            yield self.fn.value

###############################################################################
''''''
###############################################################################
