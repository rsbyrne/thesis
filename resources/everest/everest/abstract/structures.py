
###############################################################################
'''Generic funcy structures.'''
###############################################################################

from abc import abstractmethod as _abstractmethod
from collections import abc as _collabc

from .abstract import EverestABC as _EverestABC
from . import datalike as _datalike
from . import exceptions as _exceptions

class Container(_EverestABC):
    ...
_ = Container.register(_collabc.Container)

class Iterable(_EverestABC):
    ...
_ = Iterable.register(_collabc.Iterable)

class Iterator(_EverestABC):
    ...
_ = Iterator.register(_collabc.Iterator)

class Sized(_EverestABC):
    ...
_ = Sized.register(_collabc.Sized)

class Callable(_EverestABC):
    ...
_ = Callable.register(_collabc.Callable)

class Collection(Sized, Iterable, Container):
    ...
_ = Collection.register(_collabc.Collection)

class Reversible(_EverestABC):
    ...
_ = Reversible.register(_collabc.Reversible)

class Sequence(Reversible, Collection):
    ...
_ = Sequence.register(_collabc.Sequence)

class MutableSequence(Sequence):
    ...
_ = MutableSequence.register(_collabc.MutableSequence)

class Mapping(Collection):
    ...
_ = Mapping.register(_collabc.Mapping)

class Unpackable(_EverestABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Unpackable:
            if all((
                    issubclass(C, Iterable),
                    not issubclass(C, Mapping),
                    not issubclass(C, (tuple, str, _datalike.Datalike)),
                    )):
                return True
        return NotImplemented

class Struct(_EverestABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Struct:
            if all((
                    issubclass(C, Collection),
                    not issubclass(C, MutableSequence),
                    not issubclass(C, Unpackable),
                    not issubclass(C, Mapping),
                    not issubclass(C, _datalike.String),
                    )):
                return True
        return NotImplemented
    @_abstractmethod
    def __len__(self):
        raise _exceptions.AbstractMethodException

###############################################################################
###############################################################################
