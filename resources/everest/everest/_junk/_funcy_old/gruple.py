###############################################################################
''''''
###############################################################################

from collections.abc import (
    Sequence as _Sequence,
    Iterable as _Iterable,
    Mapping as _Mapping,
    )
import operator as _operator

from . import generic as _generic
from .utilities import unpacker_zip as _unpacker_zip

def strict_expose(self, ind):
    return self._incision_finalise(ind)

def flatlen(gruple):
    n = 0
    for c in gruple.pyLike:
        try:
            n += c.flatlen
        except AttributeError:
            if isinstance(c, _generic.Unpackable):
                n += len(c)
            else:
                n += 1
    return n

class _Gruple(_generic.SoftIncisable, _Sequence):

    @property
    def incisionTypes(self):
        return {
            **super().incisionTypes,
            'strict': strict_expose,
            'broad': self._swatheType
            }

    @property
    def pyLike(self): return self._pyLike
    @property
    def pyType(self): return list
    @property
    def shape(self): return (len(self.pyLike),)
    @property
    def _swatheType(self): return GrupleSwathe

    @property
    def flatlen(self):
        try:
            return self._flatlen
        except AttributeError:
            self._flatlen = _flatlen = flatlen(self)
            return _flatlen

    @classmethod
    def _rich(cls, self, other, /, *, opkey: str) -> 'Gruple':
        opfn = getattr(_operator, opkey)
        boolzip = (opfn(s, o) for s, o in _unpacker_zip(self, other))
        return cls(boolzip)
    def __lt__(self, other): return self._rich(self, other, opkey = 'lt')
    def __le__(self, other): return self._rich(self, other, opkey = 'le')
    def __eq__(self, other): return self._rich(self, other, opkey = 'eq')
    def __ne__(self, other): return self._rich(self, other, opkey = 'ne')
    def __gt__(self, other): return self._rich(self, other, opkey = 'gt')
    def __ge__(self, other): return self._rich(self, other, opkey = 'ge')

    def __repr__(self):
        return f'{type(self).__name__}{self.pyLike}'
    def __str__(self):
        return str(self.pyLike)

class Gruple(_Gruple):
    def __init__(self, arg: _Iterable):
        self._pyLike = self.pyType(arg)
        super().__init__()
    def _incision_finalise(self, arg0, /):
        return self.pyLike[arg0]

class GrupleSwathe(_generic.BroadIncision, _Gruple):
    @property
    def pyLike(self):
        return self.source.pyLike
    def __repr__(self):
        return f'Swathe({repr(self.source)}[{repr(self.incisor)}])'
    def __str__(self):
        return str(self.pyType(self))

class _GrupleMap(_Gruple, _Mapping):
    @property
    def pyType(self): return dict
    @property
    def _swatheType(self):
        return GrupleMapSwathe
    @classmethod
    def _rich(cls, self, other, /, *, opkey: str) -> 'GrupleMap':
        keys = self._keys
        if isinstance(other, _Mapping):
            keys = Gruple(k for k in keys if k in other)
            other = Gruple(other[k] for k in keys)
        vals = Gruple._rich(self._values, other, opkey = opkey)
        return cls(zip(keys, vals))

class GrupleMap(_GrupleMap, Gruple):
    def _index_sets(self): yield iter(self.pyLike)
    def _index_types(self): yield object

class GrupleMapSwathe(_GrupleMap, GrupleSwathe):
    ...

###############################################################################
''''''
###############################################################################
