###############################################################################
''''''
###############################################################################

from functools import cached_property as _cached_property
from typing import Optional as _Optional

from . import _Base, _generic

from .exceptions import *

class Dat(_Base, _generic.Incisable):
    __slots__ = ('_shape', '_context')
    def __init__(self,
            *,
            shape: tuple = (),
            context: tuple = (),
            **kwargs,
            ) -> None:
        self._shape = shape
        self._context = context
        super().__init__(
            context = self.context,
            **kwargs
            )
    @property
    def shape(self):
        return self._shape
    @property
    def context(self):
        return self._context

class DatChild(Dat):
    __slots__ = ('_parent', '_incisor')
    def __init__(self,
            parent: Dat,
            incisor: _generic.Incisor,
            /,
            *,
            context: tuple = (),
            **kwargs,
            ) -> None:
        self._parent, self._incisor = parent, incisor
        super().__init__(
            context = tuple((*context, parent)),
            incisor = incisor,
            **kwargs,
            )
    @property
    def parent(self):
        return self._parent
    @property
    def incisor(self):
        return self._incisor

class DatSam(DatChild):
    def __init__(self, parent: Dat, /, *args, **kwargs):
        super().__init__(parent, *args, shape = parent.shape, **kwargs)

class DatRed(DatChild):
    def __init__(self, parent: Dat, /, *args, **kwargs):
        super().__init__(parent, *args, shape = parent.shape[1:], **kwargs)

class QuickDat(Dat):
    __slots__ = ('_value')
    def __init__(self, value, /, **kwargs) -> None:
        self._value = value
        super().__init__(**kwargs)
    def evaluate(self) -> object:
        return self._value

###############################################################################
''''''
###############################################################################
