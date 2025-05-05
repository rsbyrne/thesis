###############################################################################
''''''
###############################################################################
from functools import lru_cache as _lru_cache
import numbers as _numbers

from . import _special

@_lru_cache(maxsize = 1000)
def fibonacci(n):
    if not isinstance(n, _numbers.Integral): raise TypeError
    if not n < _special.inf: raise ValueError
    if n == 0: return 0
    elif n == 1 or n == 2: return 1
    elif n > 2: return fibonacci(n - 1) + fibonacci(n - 2)

###############################################################################
''''''
###############################################################################
