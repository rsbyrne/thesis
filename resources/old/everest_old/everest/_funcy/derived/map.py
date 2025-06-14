###############################################################################
'''The module defining the 'Map' Derived type.'''
###############################################################################

from . import _abstract, _gruple, _Funcy

from .derived import Derived as _Derived
from .group import Group as _Group

def group_convert(arg) -> _abstract.structures.Container:
    if not isinstance(arg, _abstract.structures.Container):
        raise TypeError(type(arg))
    if isinstance(arg, _Funcy):
        return arg
    return _Group(*arg)

class Map(_Derived):
    def __init__(self, keys, values, /):
        super().__init__(*(group_convert(term) for term in (keys, values)))
    def evaluate(self, keys, values):
        return _gruple.GrupleMap(zip(keys, values))
_ = _abstract.structures.Mapping.register(_Derived)

###############################################################################
###############################################################################
