###############################################################################
'''Defines certain funcy 'special' numbers.'''
###############################################################################

from functools import wraps, total_ordering
import numbers
import sys
from collections import abc as collabc

from .exceptions import EverestException

class EverestValueError(EverestException, ValueError):
    '''Value error related to a Funcy asset.'''
class NullValueDetected(EverestValueError):
    '''Null value error related to a Funcy asset.'''
class InfiniteValueDetected(EverestValueError):
    '''Infinite value error related to a Funcy asset.'''
class UnknownValueDetected(EverestValueError):
    '''Unknown value error related to a Funcy asset.'''

class Empty(collabc.Container):
    def __iter__(self):
        yield from ()
    def __len__(self):
        return 0
    def __repr__(self):
        return 'empty'
    def __contains__(self, *_):
        return False
class EmptySequence(Empty, collabc.Sequence):
    def __getitem__(self, _):
        raise IndexError
    def __repr__(self):
        return super().__repr__() + 'seq'
class EmptyMapping(Empty, collabc.Mapping):
    def __getitem__(self, _):
        raise IndexError
    def __repr__(self):
        return super().__repr__() + 'map'
empty = Empty()
emptyseq = EmptySequence()
emptymap = EmptyMapping()

@total_ordering # Lazy - I should implement these more efficiently.
class Infinite(numbers.Number):
    def __init__(self, pos = True):
        self._posarg = pos
    def __int__(self):
        return int(InfiniteInteger(self._posarg))
    def __float__(self):
        return float(InfiniteFloat(self._posarg))
    def __lt__(self, other):
        if isinstance(other, Infinite):
            if other._posarg:
                return not self._posarg
            return self._posarg
        return not self._posarg
    def __eq__(self, other):
        if isinstance(other, Infinite):
            if other._posarg == self._posarg:
                return True
        return False

class InfiniteFloat(Infinite, float):
    def __new__(cls, *_, pos = True, **__):
        val = 'inf' if pos else '-inf'
        obj = super().__new__(cls, val)
        return obj
    def __float__(self):
        return float('inf') if self._posarg else float('-inf')
    def __repr__(self):
        return 'infflt' if float(self) > 0 else 'ninfflt'

class InfiniteInteger(Infinite, int):
    def __new__(cls, *_, pos = True, **__):
        val = sys.maxsize if pos else -sys.maxsize + 1
        obj = super().__new__(cls, val)
        return obj
    def __int__(self):
        return sys.maxsize if self._posarg else -sys.maxsize + 1

    # def __getattr__(self, key): raise InfiniteValueDetected
    # def __getitem__(self, key): raise InfiniteValueDetected
    # def __setitem__(self, key, val): raise InfiniteValueDetected

    def __add__(self, other):
        return self
    def __sub__(self, other):
        if isinstance(other, Infinite):
            raise ArithmeticError
        return self
    def __mul__(self, other):
        return self
    def __matmul__(self, other):
        return self
    def __truediv__(self, other):
        return self
    def __floordiv__(self, other):
        return self
    def __mod__(self, other):
        return self
    def __divmod__(self, other):
        return self
    def __pow__(self, other, modulo = None):
        return self
    def __lshift__(self, other):
        return self
    def __rshift__(self, other):
        return self
    def __and__(self, other):
        return True
    def __xor__(self, other):
        return True
    def __or__(self, other):
        return True

    def __radd__(self, other):
        return self
    def __rsub__(self, other):
        if isinstance(other, Infinite):
            raise ArithmeticError
        return -self
    def __rmul__(self, other):
        return self
    def __rmatmul__(self, other):
        return self
    def __rtruediv__(self, other):
        return self
    def __rfloordiv__(self, other):
        return self
    def __rmod__(self, other):
        return self
    def __rdivmod__(self, other):
        return self
    def __rpow__(self, other, modulo = None):
        return self
    def __rlshift__(self, other):
        return self
    def __rrshift__(self, other):
        return self
    def __rand__(self, other):
        return bool(other)
    def __rxor__(self, other):
        return not bool(other)
    def __ror__(self, other):
        return True

    def __iadd__(self, other):
        return self
    def __isub__(self, other):
        return self
    def __imul__(self, other):
        return self
    def __imatmul__(self, other):
        return self
    def __itruediv__(self, other):
        return self
    def __ifloordiv__(self, other):
        return self
    def __imod__(self, other):
        return self
    def __ipow__(self, other, modulo = None):
        return self
    def __ilshift__(self, other):
        return self
    def __irshift__(self, other):
        return self
    # def __iand__(self, other): return self
    # def __ixor__(self, other): return self
    # def __ior__(self, other): return self

    def __neg__(self):
        return ninf if self._posarg else inf
    def __pos__(self):
        raise NotImplementedError
    def __abs__(self):
        return inf
    def __invert__(self):
        raise NotImplementedError

    def __complex__(self):
        raise NotImplementedError

    def __index__(self):
        return 2147483647 - 1 if self._posarg else -2147483647 + 1

    def __round__(self, ndigits = 0):
        raise InfiniteValueDetected
    def __trunc__(self):
        raise InfiniteValueDetected
    def __floor__(self):
        raise InfiniteValueDetected
    def __ceil__(self):
        raise InfiniteValueDetected

    def __coerce__ (self):
        raise InfiniteValueDetected

    def __bool__(self):
        return True

    def __repr__(self):
        if self._posarg:
            return 'infint'
        return '-infint'

class BadNumber(numbers.Number):

    _error = EverestValueError

    # def __getattr__(self, key):
    #     raise self._error
    def __getitem__(self, key):
        raise self._error
    def __setitem__(self, key, val):
        raise self._error

    def __add__(self, other):
        raise self._error
    def __sub__(self, other):
        raise self._error
    def __mul__(self, other):
        raise self._error
    def __matmul__(self, other):
        raise self._error
    def __truediv__(self, other):
        raise self._error
    def __floordiv__(self, other):
        raise self._error
    def __mod__(self, other):
        raise self._error
    def __divmod__(self, other):
        raise self._error
    def __pow__(self, other, modulo = None):
        raise self._error
    def __lshift__(self, other):
        raise self._error
    def __rshift__(self, other):
        raise self._error
    def __and__(self, other):
        raise self._error
    def __xor__(self, other):
        raise self._error
    def __or__(self, other):
        raise self._error

    def __radd__(self, other):
        raise self._error
    def __rsub__(self, other):
        raise self._error
    def __rmul__(self, other):
        raise self._error
    def __rmatmul__(self, other):
        raise self._error
    def __rtruediv__(self, other):
        raise self._error
    def __rfloordiv__(self, other):
        raise self._error
    def __rmod__(self, other):
        raise self._error
    def __rdivmod__(self, other):
        raise self._error
    def __rpow__(self, other, modulo = None):
        raise self._error
    def __rlshift__(self, other):
        raise self._error
    def __rrshift__(self, other):
        raise self._error
    def __rand__(self, other):
        raise self._error
    def __rxor__(self, other):
        raise self._error
    def __ror__(self, other):
        raise self._error

    def __iadd__(self, other):
        raise self._error
    def __isub__(self, other):
        raise self._error
    def __imul__(self, other):
        raise self._error
    def __imatmul__(self, other):
        raise self._error
    def __itruediv__(self, other):
        raise self._error
    def __ifloordiv__(self, other):
        raise self._error
    def __imod__(self, other):
        raise self._error
    def __ipow__(self, other, modulo = None):
        raise self._error
    def __ilshift__(self, other):
        raise self._error
    def __irshift__(self, other):
        raise self._error
    def __iand__(self, other):
        raise self._error
    def __ixor__(self, other):
        raise self._error
    def __ior__(self, other):
        raise self._error

    def __neg__(self):
        raise self._error
    def __pos__(self):
        raise self._error
    def __abs__(self):
        raise self._error
    def __invert__(self):
        raise self._error

    def __complex__(self):
        raise self._error
    def __int__(self):
        raise self._error
    def __float__(self):
        raise self._error

    def __index__(self):
        raise self._error # for integrals

    def __round__(self, ndigits = 0):
        raise self._error
    def __trunc__(self):
        raise self._error
    def __floor__(self):
        raise self._error
    def __ceil__(self):
        raise self._error

    def __coerce__ (self):
        raise self._error

    def __lt__(self, other):
        raise self._error
    def __le__(self, other):
        raise self._error
    def __eq__(self, other):
        raise self._error
    def __ne__(self, other):
        raise self._error
    def __gt__(self, other):
        raise self._error
    def __ge__(self, other):
        raise self._error

class Null(BadNumber):
    _error = NullValueDetected
    def __repr__(self):
        return 'null'
class NullFloat(BadNumber, float):
    def __repr__(self):
        return 'nullfloat'
class NullInteger(BadNumber, int):
    def __repr__(self):
        return 'nullint'

class Unknown(BadNumber):

    _error = UnknownValueDetected

    def __add__(self, other): return self
    def __sub__(self, other): return self
    def __mul__(self, other): return self
    def __matmul__(self, other): return self
    def __truediv__(self, other): return self
    def __floordiv__(self, other): return self
    def __mod__(self, other): return self
    def __divmod__(self, other): return self
    def __pow__(self, other, modulo = None): return self
    def __lshift__(self, other): return self
    def __rshift__(self, other): return self
    def __and__(self, other): return self
    def __xor__(self, other): return self
    def __or__(self, other): return self

    def __radd__(self, other): return self
    def __rsub__(self, other): return self
    def __rmul__(self, other): return self
    def __rmatmul__(self, other): return self
    def __rtruediv__(self, other): return self
    def __rfloordiv__(self, other): return self
    def __rmod__(self, other): return self
    def __rdivmod__(self, other): return self
    def __rpow__(self, other, modulo = None): return self
    def __rlshift__(self, other): return self
    def __rrshift__(self, other): return self
    def __rand__(self, other): return self
    def __rxor__(self, other): return self
    def __ror__(self, other): return self

    def __iadd__(self, other): return self
    def __isub__(self, other): return self
    def __imul__(self, other): return self
    def __imatmul__(self, other): return self
    def __itruediv__(self, other): return self
    def __ifloordiv__(self, other): return self
    def __imod__(self, other): return self
    def __ipow__(self, other, modulo = None): return self
    def __ilshift__(self, other): return self
    def __irshift__(self, other): return self
    def __iand__(self, other): return self
    def __ixor__(self, other): return self
    def __ior__(self, other): return self

    def __neg__(self): return self
    def __pos__(self): return self
    def __abs__(self): return self

    def __round__(self, ndigits = 0): return self
    def __trunc__(self): return self
    def __floor__(self): return self
    def __ceil__(self): return self

    def __repr__(self):
        return 'unk'

class UnknownFloat(Unknown, float):
    def __repr__(self):
        return 'unkfloat'
class UnknownInteger(Unknown, int):
    def __repr__(self):
        return 'unkint'

null = Null()
nullflt = NullFloat()
nullint = NullInteger()
infint = InfiniteInteger(True)
ninfint = InfiniteInteger(False)
infflt = InfiniteFloat(True)
ninfflt = InfiniteFloat(False)
unk = Unknown()
unkflt = UnknownFloat()
unkint = UnknownInteger()

inf = infint
ninf = ninfint

# object.__add__(self, other)
# object.__sub__(self, other)
# object.__mul__(self, other)
# object.__matmul__(self, other)¶
# object.__truediv__(self, other)
# object.__floordiv__(self, other)
# object.__mod__(self, other)
# object.__divmod__(self, other)
# object.__pow__(self, other[, modulo])
# object.__lshift__(self, other)
# object.__rshift__(self, other)
# object.__and__(self, other)
# object.__xor__(self, other)
# object.__or__(self, other)
#
# object.__radd__(self, other)
# object.__rsub__(self, other)
# object.__rmul__(self, other)
# object.__rmatmul__(self, other)
# object.__rtruediv__(self, other)
# object.__rfloordiv__(self, other)
# object.__rmod__(self, other)
# object.__rdivmod__(self, other)
# object.__rpow__(self, other[, modulo])
# object.__rlshift__(self, other)
# object.__rrshift__(self, other)
# object.__rand__(self, other)
# object.__rxor__(self, other)
# object.__ror__(self, other)
#
# object.__iadd__(self, other)
# object.__isub__(self, other)
# object.__imul__(self, other)
# object.__imatmul__(self, other)
# object.__itruediv__(self, other)
# object.__ifloordiv__(self, other)
# object.__imod__(self, other)
# object.__ipow__(self, other[, modulo])
# object.__ilshift__(self, other)
# object.__irshift__(self, other)
# object.__iand__(self, other)
# object.__ixor__(self, other)
# object.__ior__(self, other)
#
# object.__neg__(self)
# object.__pos__(self)
# object.__abs__(self)
# object.__invert__(self)
#
# object.__complex__(self)
# object.__int__(self)
# object.__float__(self)
#
# object.__index__(self) # for integrals
#
# object.__round__(self[, ndigits])
# object.__trunc__(self)
# object.__floor__(self)
# object.__ceil__(self)

###############################################################################
''''''
###############################################################################
