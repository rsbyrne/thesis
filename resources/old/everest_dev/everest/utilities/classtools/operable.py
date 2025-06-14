###############################################################################
''''''
###############################################################################

from abc import abstractmethod as _abstractmethod
import operator as _operator
from functools import partial as _partial, lru_cache as _lru_cache

from . import _misc
_ARITHMOPS = _misc.ARITHMOPS
_RICHOPS = _misc.RICHOPS
_REVOPS = _misc.REVOPS
OPS = (*_ARITHMOPS, *_RICHOPS, *_REVOPS)

from .adderclass import AdderClass as _AdderClass


class Operable(_AdderClass):

    @_AdderClass.decorate(classmethod)
    @_AdderClass.decorate(_lru_cache(maxsize = 32))
    def get_operator(cls, operator):  # pylint: disable=E0213,R0201
        if isinstance(operator, str):
            if operator in OPS:
                if operator in _REVOPS:
                    raise ValueError
                    # operator = operator[1:]
                    # operands = operands[::-1]
                operator = getattr(_operator, f"__{operator}__")
            else:
                raise KeyError(operator)
        return operator

    @_AdderClass.decorate(classmethod)
    @_AdderClass.decorate(_abstractmethod)
    def operate(cls, operator, *args, **kwargs) -> object:  # pylint: disable=E0213 R0201
        '''Carries out the actual operation and returns the result.'''
        raise TypeError(
            "This method is abstract and should never be called."
            )

    def _op(self, other = None, /, *, operator, rev = False, **kwargs):
        operator = self.get_operator(operator)
        if other is None:
            return self.operate(operator, self, **kwargs)
        if rev:
            return self.operate(operator, other, self, **kwargs)
        return self.operate(operator, self, other, **kwargs)

    def apply(self, operator, **kwargs):
        return self._op(operator = operator, **kwargs)
    @_AdderClass.decorate(_lru_cache(maxsize = 64))
    def transform(self, operator, **kwargs):
        return _partial(self._op, operator = operator, **kwargs)

    ### BINARY ###

    def __add__(self, other):
        return self._op(other, operator = 'add')
    def __sub__(self, other):
        return self._op(other, operator = 'sub')
    def __mul__(self, other):
        return self._op(other, operator = 'mul')
    def __matmul__(self, other):
        return self._op(other, operator = 'matmul')
    def __truediv__(self, other):
        return self._op(other, operator = 'truediv')
    def __floordiv__(self, other):
        return self._op(other, operator = 'floordiv')
    def __mod__(self, other):
        return self._op(other, operator = 'mod')
    def __divmod__(self, other):
        return self._op(other, operator = 'divmod')
    def __pow__(self, other):
        return self._op(other, operator = 'pow')
    # def __lshift__(self, other):
    #     return self._op(other, operator = 'lshift')
    # def __rshift__(self, other):
    #     return self._op(other, operator = 'rshift')
    def __and__(self, other):
        return self._op(other, operator = 'and')
    def __or__(self, other):
        return self._op(other, operator = 'or')
    def __xor__(self, other):
        return self._op(other, operator = 'xor')

    #### BINARY REVERSED ####

    def __radd__(self, other):
        return self._op(other, operator = 'add', rev = True)
    def __rsub__(self, other):
        return self._op(other, operator = 'sub', rev = True)
    def __rmul__(self, other):
        return self._op(other, operator = 'mul', rev = True)
    def __rmatmul__(self, other):
        return self._op(other, operator = 'matmul', rev = True)
    def __rtruediv__(self, other):
        return self._op(other, operator = 'truediv', rev = True)
    def __rfloordiv__(self, other):
        return self._op(other, operator = 'floordiv', rev = True)
    def __rmod__(self, other):
        return self._op(other, operator = 'mod', rev = True)
    def __rdivmod__(self, other):
        return self._op(other, operator = 'divmod', rev = True)
    def __rpow__(self, other):
        return self._op(other, operator = 'pow', rev = True)
    # def __rlshift__(self, other):
    #     return self._op(other, operator = 'lshift', rev = True)
    # def __rrshift__(self, other):
    #     return self._op(other, operator = 'rshift', rev = True)
    def __rand__(self, other):
        return self._op(other, operator = 'and', rev = True)
    def __ror__(self, other):
        return self._op(other, operator = 'xor', rev = True)
    def __rxor__(self, other):
        return self._op(other, operator = 'or', rev = True)

    #### UNARY ####

    def __neg__(self):
        return self._op(operator = 'neg')
    def __pos__(self):
        return self._op(operator = 'pos')
    # def __abs__(self):
    #     return self._op(operator = 'abs')
    # def __invert__(self):
    #     return self._op(operator = 'invert')
    # def __ceil__(self):
    #     return self._op(operator = 'ceil')
    # def __floor__(self):
    #     return self._op(operator = 'floor')
    # def __round__(self, ndigits):
    #     return self._op(operator = 'round', ndigits = int(ndigits))
    # def __trunc__(self):
    #     return self._op(operator = 'trunc')
    # def __float__(self):
    #     return self._op(operator = 'float')
    # def __int__(self):
    #     return self._op(operator = 'int')
    # def __complex__(self):
    #     return self._op(operator = 'complex')
    # def __str__(self):
    #     return self._op(operator = 'str')
    # def __index__(self):
    #     return self._op(operator = 'index')

    #### BOOLEAN ####

    @_AdderClass.forcemethod
    def __lt__(self, other):
        return self._op(other, operator = 'lt', typ = bool)
    @_AdderClass.forcemethod
    def __le__(self, other):
        return self._op(other, operator = 'le', typ = bool)
    @_AdderClass.forcemethod
    def __eq__(self, other):
        return self._op(other, operator = 'eq', typ = bool)
    @_AdderClass.forcemethod
    def __ne__(self, other):
        return self._op(other, operator = 'ne', typ = bool)
    @_AdderClass.forcemethod
    def __gt__(self, other):
        return self._op(other, operator = 'gt', typ = bool)
    @_AdderClass.forcemethod
    def __ge__(self, other):
        return self._op(other, operator = 'ge', typ = bool)


###############################################################################
###############################################################################
