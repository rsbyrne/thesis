###############################################################################
''''''
###############################################################################

import itertools as _itertools
from collections.abc import Iterable as _Iterable, Mapping as _Mapping

from . import _generic, _GrupleMap, _unpacker_zip
from .group import Group as _Group, groups_resolve
from .derived import Derived as _Derived

from .exceptions import *

class Map(_Derived, _generic.Mapping):

    def __init__(self, keys, values, /, **kwargs) -> None:
        keys, values = (self._group_convert(t) for t in (keys, values))
        super().__init__(keys, values, **kwargs)
        self._keys, self._values = self.terms

    @staticmethod
    def _group_convert(arg) -> _generic.Container:
        if isinstance(arg, _generic.Evaluable):
            if isinstance(arg, _generic.Container):
                return arg
        else:
            if isinstance(arg, _Iterable):
                return _Group(*arg)
        raise TypeError(type(arg))

    def _evaluate(self, terms) -> object:
        return _GrupleMap(_unpacker_zip(*terms))

    @property
    def rawValue(self) -> _GrupleMap:
        assert not self.isSeq
        return _GrupleMap(
            _unpacker_zip(*(groups_resolve(t) for t in self.terms))
            )
    def rawValues(self):
        return self.rawValue.values()
    def rawItems(self):
        return self.rawValue.items()

    def __setitem__(self,
            ind: _generic.ShallowIncisor, val : object, /
            ) -> None:
        ind, val = self._value_resolve(ind), self._value_resolve(val)
        toSet = self.rawValue[ind]
        if isinstance(ind, _generic.StrictIncisor):
            toSet.value = val
        else:
            if isinstance(val, _generic.Unpackable):
                val = val[ind]
            for s, v in _unpacker_zip(toSet, val):
                s.value = v
    def __delitem__(self, ind: _generic.ShallowIncisor, /) -> None:
        self[ind] = None
    def _set_value(self, val, /) -> None:
        self.__setitem__(..., val)

    def __iter__(self):
        return self._keys.__iter__()
    def __len__(self):
        return len(self.rawValue)

    def keys(self):
        return self.rawValue.keys()
    def values(self):
        return self.rawValue.values()
    def items(self):
        return self.rawValue.items()

###############################################################################
''''''
###############################################################################
