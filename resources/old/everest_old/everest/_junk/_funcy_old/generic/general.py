###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod

from .exceptions import *

class Generic(_ABC):
    ...

class NoneType(Generic):
    ...
_ = NoneType.register(type(None))

class Slice(Generic):
    @_abstractmethod
    def indices(self, length: int, /) -> tuple:
        raise AbstractMethodException
    def iterable(self, length):
        return range(*self.indices(length))
_ = Slice.register(slice)

class Evaluable(Generic):
    @property
    @_abstractmethod
    def value(self):
        raise AbstractMethodException

class Variable(Evaluable):
    @property
    @_abstractmethod
    def value(self) -> object:
        raise AbstractMethodException
    @value.setter
    @_abstractmethod
    def value(self, val, /) -> None:
        raise AbstractMethodException
    @value.deleter
    def value(self) -> None:
        self.value = None

###############################################################################
''''''
###############################################################################
