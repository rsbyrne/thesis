from functools import cached_property, lru_cache
import numbers
from everest.funcy import inf

@lru_cache(maxsize = 1000)
def fibonacci(n):
    if not isinstance(n, numbers.Integral): raise TypeError
    if not n < inf: raise ValueError
    if n == 0: return 0
    elif n == 1 or n == 2: return 1
    elif n > 2: return fibonacci(n - 1) + fibonacci(n - 2)
