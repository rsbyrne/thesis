###############################################################################
''''''
###############################################################################


import string as _string
import warnings as _warnings
import hashlib as _hashlib
import time as _time
from functools import (
    lru_cache as _lru_cache, wraps as _wraps, partial as _partial
    )
from collections import deque as _deque

import numpy as _np
from numpy.random import SeedSequence, default_rng

from . import exceptions as _exceptions


@_lru_cache
def get_seed(seed):
    if isinstance(seed, int):
        return seed
    return int(_hashlib.md5(repr(seed).encode()).hexdigest(), 16)


class ReseedException(_exceptions.EverestException):
    '''Something went wrong with a Reseed object.'''

def multi(func):
    @_wraps(func)
    def wrapper(*args, n, **kwargs):
        return tuple(func(*args, **kwargs) for _ in range(n))
    return wrapper

class Reseed:

    __slots__ = ('seed', 'rng', 'initstate', 'priorstates', 'random')

    def __init__(self, seed = None, /):
        seed = self.seed = get_seed(seed)
        rng = self.rng = default_rng(SeedSequence(self.seed))
        self.initstate = self.__getstate__()
        self.priorstates = _deque()
        self.random = rng.random

    def __getstate__(self):
        return self.rng.__getstate__()
    def __setstate__(self, state):
        self.rng.__setstate__(state)
    def _reset(self):
        self.__setstate__(self.initstate)
    def _save_state(self):
        self.priorstates.append(self.__getstate__())
    def _restore_state(self):
        self.__setstate__(self.priorstates.pop())
    def reset(self):
        if self.priorstates:
            raise ReseedException("Cannot reset when there are prior states.")
        self._reset()

    def __enter__(self):
        self._save_state()
        self._reset()
        return self
    def __exit__(self, *args):
        self._restore_state()

    def __getattr__(self, name):
        return getattr(self.rng, name)

    def rbool(self):
        return bool(self.rng.integers(0, 1))
    rbools = multi(rbool)

    def rint(self, /, low = 0, high = 9):
        if high > (highest := 2 ** 63):
            _warnings.warn("High is too high; capping at 2 ** 63.")
            high = min(high, highest)
        return int(self.rng.integers(low, high))
    rints = multi(rint)

    def rshade(self, /):  # pylint: disable=R0201
        return rint(0, 255)
    rshades = multi(rshade)
    rcolour = _partial(rshades, n = 3)
    rcolours = multi(rcolour)

    def rdigits(self, /, n = 12, **kwargs):
        low = int(10 ** n)
        high = int(10 ** (n + 1)) - 1
        return self.rint(low, high, **kwargs)

    def rfloat(self, /, low = 0., high = 1.):
        return float(self.random() * (high - low) + low)
    rfloats = multi(rfloat)

    def rval(self, /, low = 0., high = 1., **kwargs):
        return type(low)(self.rfloat(low, high, **kwargs))
    rvals = multi(rval)

    def rarray(self, /, low = 0., high = 1., shape = (1,), dtype = None):
        if dtype is None:
            dtype = type(low)
        return (self.random(*shape) * (high - low) + low).astype(dtype)
    rarrays = multi(rarray)

    def rangearr(self, /, lows, highs = None):
        try:
            lows = _np.array(lows)
            if highs is None:
                lows, highs = (a.squeeze() for a in _np.split(lows, 2, -1))
            else:
                highs = _np.array(highs)
            return _np.array(
                lows + self.random(*lows.shape) * (highs - lows),
                dtype = lows.dtype
                )
        except Exception as exc:
            if not all(isinstance(a, _np.ndarray) for a in (lows, highs)):
                raise TypeError(type(lows), type(highs)) from exc
            if not lows.shape == highs.shape:
                raise ValueError(lows.shape, highs.shape) from exc
            if not lows.dtype == highs.dtype:
                raise ValueError(lows.dtype, highs.dtype) from exc
            raise exc
    rangearrs = multi(rangearr)

    def rchoice(self, /, population, selections = 1):
        if isinstance(population, str):
            population = list(population)
        if selections > 1:
            return tuple(self.rng.choice(population) for i in range(selections))
        return self.rng.choice(population)

    def rshuffle(self, *args, **kwargs):
        return self.rng.shuffle(*args, **kwargs)

    def rstr(self, /, length = 16):
        letters = _string.ascii_lowercase
        return ''.join(self.rchoice(letters, length))
    rstrs = multi(rstr)

    def rsleep(self, /, low = 0.5, high = 1.5, **kwargs):
        _time.sleep(self.rfloat(low, high, **kwargs))


GLOBALRAND = Reseed(None)

def reseed(func):
    @_wraps(func)
    def wrapper(*args, seed = GLOBALRAND, **kwargs):
        if isinstance(rng := seed, Reseed):
            return func(rng, *args, **kwargs)
        with Reseed(seed) as rng:
            return func(rng, *args, **kwargs)
    return wrapper

rint = reseed(Reseed.rint)
rints = reseed(Reseed.rints)
rshade = reseed(Reseed.rshade)
rshades = reseed(Reseed.rshades)
rcolour = reseed(Reseed.rcolour)
rcolours = reseed(Reseed.rcolours)
rdigits = reseed(Reseed.rdigits)
rfloat = reseed(Reseed.rfloat)
rfloats = reseed(Reseed.rfloats)
rval = reseed(Reseed.rval)
rvals = reseed(Reseed.rvals)
rarray = reseed(Reseed.rarray)
rarrays = reseed(Reseed.rarrays)
rangearr = reseed(Reseed.rangearr)
rangearrs = reseed(Reseed.rangearrs)
rchoice = reseed(Reseed.rchoice)
rshuffle = reseed(Reseed.rshuffle)
rsleep = reseed(Reseed.rsleep)
rstr = reseed(Reseed.rstr)
rstrs = reseed(Reseed.rstrs)

###############################################################################

# rsd = reseed.Reseed(1066)
# print(rsd.random())
# print(rsd.random())
# rsd.reset()
# print(rsd.random())
# print(rsd.random())
# with rsd:
#     print(rsd.random())
#     print(rsd.random())
#     with rsd:
#         print(rsd.random())
#         print(rsd.random())
#     try:
#         rsd.reset()
#         raise Exception
#     except:
#         pass
#     print(rsd.random())
#     print(rsd.random())
# print(rsd.random())
# print(rsd.random())

###############################################################################
