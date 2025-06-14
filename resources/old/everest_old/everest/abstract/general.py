###############################################################################
'''General-purpose abstract classes.'''
###############################################################################

from abc import abstractmethod as _abstractmethod

from .abstract import EverestABC as _EverestABC
from .exceptions import AbstractMethodException

class Evaluable(_EverestABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Evaluable:
            if any('value' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

def evaluable(arg):
    return isinstance(arg, Evaluable)

class Variable(Evaluable):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Variable:
            if any('set_value' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

class NoneType(_EverestABC):
    ...
_ = NoneType.register(type(None))

class Slice(_EverestABC):
    @_abstractmethod
    def indices(self, length: int, /) -> tuple:
        raise AbstractMethodException
    def iterable(self, length):
        return range(*self.indices(length))
_ = Slice.register(slice)

###############################################################################
###############################################################################
