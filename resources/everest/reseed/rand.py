import random
import string
import warnings
import hashlib
from functools import cached_property, lru_cache, wraps

import numpy as np
from numpy.random import SeedSequence, default_rng

GLOBALSEED = 0

@lru_cache
def _get_seed(seed):
    if type(seed) is int: return seed
    else: return int(hashlib.md5(repr(seed).encode()).hexdigest(), 16)

class _MetaReseed(type):
    @lru_cache
    def __getattr__(cls, name):
        return reseed_func(name)
class Reseed(metaclass = _MetaReseed):
    rng = None
    __slots__ = ('seed', 'oldState', 'oldRng',)
    def __init__(self, seed = None):
        if seed is None:
            global GLOBALSEED
            seed = GLOBALSEED
            GLOBALSEED += 1
        else:
            seed = _get_seed(seed)
        self.seed = seed
    def __enter__(self):
        self.oldState = random.getstate()
        self.oldRng = Reseed.rng
        random.seed(self.seed)
        Reseed.rng = default_rng(SeedSequence(self.seed))
        return self
    def __exit__(self, *args):
        random.setstate(self.oldState)
        Reseed.rng = self.oldRng
    def __getattr__(self, name):
        try:
            return getattr(self.rng, name)
        except AttributeError:
            return getattr(random, name)

def _find_func(*names, source = None):
    if source is None:
        try:
            target = np.random
            return _recursive_get(target, *names)
        except AttributeError:
            target = random
            return _recursive_get(target, *names)
    else:
        target = source
        return _recursive_get(target, *names)
def _recursive_get(target, *names):
    for name in names:
        target = getattr(target, name)
    return target
def reseed_func(*names):
    fn = _find_func(*names)
    @wraps(fn)
    def wrapper(*args, seed = None, **kwargs):
        with Reseed(seed):
            return _find_func(*names, source = Reseed.rng)(*args, **kwargs)
    return wrapper

def reseed(func):
    @wraps(func)
    def wrapper(*args, seed = None, **kwargs):
        with Reseed(seed):
            return func(*args, **kwargs)
    return wrapper

@reseed
def randint(low = 0, high = 9):
    return random.randint(low, high)
def digits(n = 16, **kwargs):
    low = int(10 ** n)
    high = int(10 ** (n + 1)) - 1
    return randint(low, high, **kwargs)
@reseed
def randfloat(low = 0., high = 1.):
    return random.random() * (high - low) + low
def randval(low = 0., high = 1., **kwargs):
    return type(low)(randfloat(low, high, **kwargs))
@reseed
def array(low = 0., high = 1., shape = (1,), dtype = None):
    if dtype is None: dtype = type(low)
    return (Reseed.rng.random(*shape) * (high - low) + low).astype(dtype)
@reseed
def rangearr(lows, highs = None):
    try:
        lows = np.array(lows)
        if highs is None:
            lows, highs = (a.squeeze() for a in np.split(lows, 2, -1))
        else:
            highs = np.array(highs)
        return np.array(
            lows + Reseed.rng.random(*lows.shape) * (highs - lows),
            dtype = lows.dtype
            )
    except Exception as e:
        if not all(type(a) is np.ndarray for a in (lows, highs)):
            raise TypeError(type(lows), type(highs))
        if not lows.shape == highs.shape:
            raise ValueError(lows.shape, highs.shape)
        if not lows.dtype == highs.dtype:
            raise ValueError(lows.dtype, highs.dtype)
        raise e
@reseed
def arrchoice(pop, sel = 1, replace = True, p = None):
    return Reseed.rng.choice(pop, sel, replace = replace, p = p)
def sleep(low = 0.5, high = 1.5, **kwargs):
    time.sleep(randfloat(low, high, **kwargs))
@reseed
def choice(population, selections = 1):
    if selections > 1:
        return (random.choice(population) for i in range(selections))
    else:
        return random.choice(population)
@reseed
def randstring(length = 16):
    letters = string.ascii_lowercase
    return ''.join(choice(letters, length))
