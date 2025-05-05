###############################################################################
''''''
###############################################################################

from abc import ABCMeta as _ABCMeta
from collections import abc as _collabc
from itertools import repeat as _repeat
from functools import partial as _partial, lru_cache as _lru_cache
from types import FunctionType as _FunctionType

from . import _special, _classtools

from .exceptions import (
    DimensionUniterable, DimensionInfinite
    )


def raise_uniterable():
    raise DimensionUniterable

def show_iter_vals(iterable):
    i, ii = list(iterable[:6]), list(iterable[:7])
    content = ', '.join(str(v) for v in i)
    if len(ii) > len(i):
        content += ' ...'
    return f'[{content}]'

def pattern_get(dim, pattern):
    return dim[dim.apply(pattern)]


class DimensionMeta(_ABCMeta):
    ...

@_classtools.Diskable
@_classtools.MROClassable
@_classtools.Operable
class Dimension(metaclass = DimensionMeta):

    __slots__ = (
        '__dict__', 'iterlen', 'source', '_sourceget_', '_repr',
        )
    mroclasses = ('Iterator', 'Derived', 'Transform', 'Slice', 'Collapsed')

    typ = object
    collapsed = False

    iter_fn = staticmethod(raise_uniterable)

    def calculate_len(self):
        i = None
        for i, _ in enumerate(zip(self, range(int(1e9)))):
            continue
        if i is None:
            return 0
        if i == int(1e9) - 1:
            return _special.inf
        return i + 1

    def determine_type(self):
        return type(next(iter(self)))

    def __init__(self, typ = None):
        if not hasattr(self, 'iterlen'):
            self.iterlen = self.calculate_len()
        if typ is None:
            if self.typ is object:
                self.typ = self.determine_type()
        else:
            if not (styp := self.typ) is object:
                raise ValueError(
                    f"Multiple values interpreted for typ: {typ, styp}"
                    )
            self.typ = typ
        super().__init__()

    @property
    def tractable(self):
        return self.iterlen < _special.inf

    def count(self, value):
        if not self.tractable:
            raise ValueError("Cannot count occurrences in infinite iterator.")
        i = 0
        for val in self:
            if val == value:
                i += 1
        return i

    def _iter(self):
        return self.Iterator(self.iter_fn)
    def __iter__(self):
        return self._iter()

    def __len__(self):
        if isinstance(iterlen := self.iterlen, _special.InfiniteInteger):
            raise DimensionInfinite
        return iterlen

    @classmethod
    def getmeths(cls):
        yield _FunctionType, pattern_get
        yield type(NotImplemented), lambda dim, inc: dim

    @classmethod
    @_lru_cache(maxsize = 64)
    def choose_getmeth(cls, typ, /):
        for comptyp, meth in cls.getmeths():
            if issubclass(typ, comptyp):
                return meth
        return cls.Collapsed

    def __getitem__(self, arg, /):
        return self.choose_getmeth(type(arg))(self, arg)

    def __bool__(self):
        return self.iterlen > 0

    def get_valstr(self):
        if self.iterlen <= 7:
            return str(list(self))[1:-1]
        start = str(list(self[:3]))[1:-1]
        if self.tractable:
            end = str(list(self[-2:]))[1:-1]
            return f"{start}, ... {end}"
        return f"{start}"
    def get_repr(self):
        return f"{type(self).__name__} == [{self.get_valstr()}]"
    def __repr__(self):
        try:
            return self._repr
        except AttributeError:
            _repr = self._repr = self.get_repr() # pylint: disable=W0201
            return _repr

    class Iterator(_collabc.Iterator):
        __slots__ = ('gen',)
        def __init__(self, iter_fn, /):
            self.gen = iter_fn()
            super().__init__()
        def __next__(self):
            return next(self.gen)
        def __repr__(self):
            return f"{__class__.__name__}({repr(self.gen)})"

    @_classtools.Overclass
    class Derived:
        fixedoverclass = None
        def __init__(self, *sources, **kwargs):
            source = None
            for source in sources:
                if isinstance(source, Dimension):
                    break
            if source is None:
                raise TypeError(
                    f"Source must be Dimension type, not {type(source)}"
                    )
            self.source = source
            if hasattr(source, '_sourceget_'):
                self._sourceget_ = source._sourceget_
            else:
                self._sourceget_ = type(source).__getitem__
            super().__init__(**kwargs)
            self.register_argskwargs(*sources) # pylint: disable=E1101
        def __getitem__(self, arg):
            return self._sourceget_(self, arg)
        def choose_getmeth(self, typ):
            return self.source.choose_getmeth(typ)

    class Transform(Derived):
        def __init__(self, operator, /, *operands, **kwargs):
            self.operands, self.operator = operands, operator
            isdim = tuple(isinstance(op, Dimension) for op in operands)
            nisdim = isdim.count(True)
            if all(isdim):
                self.iter_fn = _partial(map, operator, *operands)
            elif not nisdim:
                raise ValueError("No dims in input!")
            else:
                if nisdim == 1:
                    self.iterlen = operands[isdim.index(True)].iterlen
                getops = lambda: (
                    op if isinstance(op, Dimension) else _repeat(op)
                        for op in operands
                    )
                self.iter_fn = _partial(map, operator, *getops())
            super().__init__(operator, *operands, **kwargs)
    @classmethod
    def operate(cls, *args, **kwargs):
        return cls.Transform(*args, **kwargs)

    class Incision(Derived):
        def __init__(self, source, incisor, /, **kwargs):
            self.source, self.incisor = source, incisor
            super().__init__(source, **kwargs)
            self.register_argskwargs(incisor) # pylint: disable=E1101

    class Collapsed(Incision):

        collapsed = True

        def __init__(self, dim, ind, **kwargs):
            self.ind, self._value, self.iterlen = ind, None, 1
            # self.iter_fn = _partial(iter, _partial(getattr, self, 'value'))
            self.iterlen = 1
            super().__init__(dim, ind, **kwargs)

        def __iter__(self):
            yield self.value

        @property
        def value(self):
            if (val := self._value) is None:
                for ind, val in enumerate(self.source):
                    if ind == self.ind:
                        break
                self._value = val
            return val

    @classmethod
    def construct(cls, arg):
        return cls(arg)

###############################################################################
###############################################################################
