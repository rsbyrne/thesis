###############################################################################
'''The module defining the top-level 'incisable' types.'''
###############################################################################

from collections import abc as _collabc
from functools import (
    partial as _partial,
    lru_cache as _lru_cache,
    )
import itertools as _itertools
from abc import (
    ABC as _ABC,
    )

from . import _special, _abstract, _mroclasses

from . import incisor as _incisor
from . import incision as _incision

def null_fn(*args, **kwargs):
    return args, kwargs

@_mroclasses.MROClassable
class Incisable(_ABC):
    _length = NotImplemented
    _maxcount = 1_000_000
    _depth = _special.infint
    _sub = None
    # Incision types
    Sub = _incision.SubIncision
    Deep = _incision.DeepIncision
    Broad = _incision.BroadIncision
    Strict = _incision.StrictIncision
    def __init__(self, *args, lev = None, **kwargs):
        subkw = self._subkwargs = dict()
        if not lev is None:
            if isinstance(lev, tuple):
                depth = len(lev)
                lev, *levn = lev
                subkw['lev'] = tuple(levn)
            else:
                depth = 1
            self._length = lev
            self._depth = depth
        super().__init__(*args, **kwargs)
    @property
    def subkwargs(self):
        return self._subkwargs
    @classmethod
    def _incision_methods(cls):
        yield from (
            (_abstract.general.Evaluable, cls._getitem_evaluable),
            (_collabc.Generator, cls._getitem_generator),
            (_incisor.TrivialIncisor, cls._getitem_trivial),
            (_incisor.SubIncisor, cls.Sub),
            (_incisor.DeepIncisor, cls.Deep),
            (_incisor.StrictIncisor, cls.Strict),
            (_incisor.BroadIncisor, cls.Broad),
            )
    @classmethod
    @_lru_cache(maxsize = 32)
    def get_incision_method(cls, arg, /):
        for typ, meth in cls._incision_methods():
            if issubclass(arg, typ):
                return meth
        return NotImplemented
    def __getitem__(self, arg: _incisor.Incisor, /):
        incmeth = self.get_incision_method(type(arg))
        if incmeth is NotImplemented:
            raise TypeError(arg, type(arg))
        return incmeth(self, arg)
    def _getitem_generator(self, arg):
        return self[list(arg)]
    def _getitem_evaluable(self, arg, /):
        return self[arg.value]
    def _getitem_trivial(self, _):
        return self
    def __call__(self, arg0, /, *argn):
        if not argn:
            return arg0
        return tuple((arg0, *argn))
    def _get_end_info(self):
        raise TypeError(f"Cannot index type {type(self)}")
    @property
    def length(self):
        if (length := self._length) is None:
            length, _ = self._get_end_info()
        return length
    def lengths(self):
        yield self.length
    @property
    def shape(self):
        return tuple(self.lengths)
    @property
    def depth(self):
        return self._depth
    def levels(self):
        yield self
    @property
    def levelsdict(self):
        return dict(enumerate(self.levels()))
    def _get_level(self, i):
        try:
            return self.levelsdict[i]
        except KeyError:
            return None
    @property
    def nlevels(self):
        return len(self.levelsdict)
    @property
    def tractable(self):
        return not isinstance(
            self.length,
            (_special.Unknown, _special.Infinite,
            _special.BadNumber, type(NotImplemented)),
            )
    def __len__(self):
        if self.tractable:
            return self.length
        raise ValueError("Cannot measure length of this object.")
    def indices(self):
        raise TypeError(f"Cannot index type {type(self)}")

def safe_iterate(iterator, maxcount):
    iterator = enumerate(iterator)
    count, iterant = None, None
    for count, iterant in iterator:
        if count > maxcount:
            raise RuntimeError("Max count exceeded on incision iter.")
        yield count, iterant

class SoftIncisable(Incisable):

    _endind = None
    _endval = None
    _length = _special.infint

    Soft = _incision.SoftIncision

    @classmethod
    def _incision_methods(cls):
        yield (_incisor.SoftIncisor, cls._getitem_soft)
        yield (_incisor.StrictIncisor, cls._getitem_strict)
        yield from super()._incision_methods()
    def _getitem_strict(self, arg, /):
        indi = self.get_indi(arg)
        for inds in self.allindices():
            if arg == inds[indi]:
                return self.Strict(inds[0], self)
        raise IndexError(arg)
    def _getitem_soft(self, arg, /):
        if isinstance(arg, slice):
            if arg == slice(None):
                return self
        return self.Soft(arg, self)

    def index_sets(self) -> 'Generator[Generator]':
        try:
            yield range(self._length)
        except (ValueError, TypeError):
            yield _itertools.count()
    def index_types(self) -> 'Generator[type]':
        yield _abstract.datalike.Integral
    def get_indi(self, arg, /):
        argtyp = type(arg)
        for i, typ in list(enumerate(self.index_types()))[::-1]:
            if issubclass(argtyp, typ):
                return i
        raise TypeError(
            f"Incisor type {type(self)}"
            f" cannot be incised by arg type {type(arg)}"
            )
    def allindices(self) -> 'Generator[tuple]':
        return zip(*self.index_sets())
    def indices(self):
        return iter(next(self.index_sets()))
    def __iter__(self):
        return (
            self(ind)
                for _, ind in safe_iterate(
                    self.indices(),
                    self._maxcount,
                    )
            )
    def _get_end_info(self):
        length, endind = None, None
        try:
            iterator = safe_iterate(self.allindices(), self._maxcount)
            for length, endind in iterator:
                ...
            if length is None:
                length = 0
            else:
                length += 1
        except RuntimeError:
            length, endind = _special.unkint, _special.unkint
        self._length, self._endind = length, endind
        return length, endind
    @property
    def endind(self):
        if (endind := self._endind) is None:
            _, endind = self._get_end_info()
        return endind
    @property
    def endval(self):
        if (endval := self._endval) is None:
            endval = self._endval = self(self.endind[0])
        return endval

###############################################################################
###############################################################################
