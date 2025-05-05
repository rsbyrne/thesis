###############################################################################
''''''
###############################################################################

from functools import cached_property as _cached_property
import weakref as _weakref

from . import _wordhash, _reseed
from . import utilities as _utilities, generic as _generic
from . gruple import Gruple as _Gruple, GrupleMap as _GrupleMap

from .exceptions import *

# class NameProxy(cls):
#     def __init__(self, cls, *terms, **kwargs):
#         self.cls, self.terms, self.kwargs = cls, terms, kwargs
#     @property
#     def kwargstr(self):
#         return self.cls._kwargstr(self)
#     @property
#     def titlestr(self):
#         return self.cls._titlestr(self)
#     @property
#     def namestr(self):
#         return self.cls._namestr(self)
#     @property
#     def hashID(self):
#         return self.cls._hashID(self)

class Function(_generic.Evaluable):

    __slots__ = (
        'kwargs',
#         '__weakref__',
#         '__dict__',
        )

    unique = False

    _premade = _weakref.WeakValueDictionary()

    @classmethod
    def _value_resolve(cls, val):
        while True:
            try:
                val = val.value
            except AttributeError:
                break
        return val

    @classmethod
    def _construct(cls, *terms, unique = False, **kwargs):
        prox = cls(*terms, **kwargs)
        if (unique or cls.unique):
            return cls(*terms, **kwargs)
        else:
            try:
                return cls._premade[prox.hashID]
            except KeyError:
                cls._premade[prox.hashID] = prox
                return prox

    def __init__(self, indices = None, **kwargs):
        if not all(isinstance(v, _generic.Primitive) for v in kwargs.values()):
            raise TypeError(kwargs)
        self.kwargs = kwargs
        if not indices is None: self.indices = indices
        super().__init__()

    @_cached_property
    def _Fn(self):
        from .constructor import Fn as _Fn
        return _Fn

    class _Prx:
        __slots__ = ('_host')
        def __init__(self, host):
#             self._host = _weakref.ref(host)
            self._host = host
        @property
        def host(self):
#             return self._host()
            return self._host
        @property
        def _Fn(self):
            return self.host._Fn
        def __repr__(self):
            return f"funcy.Function._{self.__name__}({repr(self.host)})"

    class _V(_Prx):

        """This object defers almost all calls made to it"""
        """ to the underlying value."""
        """ Use it to easily construct large Function objects."""

        def op(self, *args, rev = False, **kwargs):
            if rev: return self._Fn.op(*(*args, self.host), **kwargs)
            else: return self._Fn.op(self.host, *args, **kwargs)

        ### OPERATORS ###

        #### BINARY ####

        def __add__(self, other):
            return self.op(other, opkey = 'add')
        def __sub__(self, other):
            return self.op(other, opkey = 'sub')
        def __mul__(self, other):
            return self.op(other, opkey = 'mul')
        def __matmul__(self, other):
            return self.op(other, opkey = 'matmul')
        def __truediv__(self, other):
            return self.op(other, opkey = 'truediv')
        def __floordiv__(self, other):
            return self.op(other, opkey = 'floordiv')
        def __mod__(self, other):
            return self.op(other, opkey = 'mod')
        def __divmod__(self, other):
            return self.op(other, opkey = 'divmod')
        def __pow__(self, other):
            return self.op(other, opkey = 'pow')
        def __lshift__(self, other):
            return self.op(other, opkey = 'lshift')
        def __rshift__(self, other):
            return self.op(other, opkey = 'rshift')
        def __and__(self, other):
            return self.op(other, opkey = 'and')
        def __xor__(self, other):
            return self.op(other, opkey = 'or')
        def __or__(self, other):
            return self.op(other, opkey = 'xor')

        #### BINARY REVERSED ####

        def __radd__(self, other):
            return self.op(other, opkey = 'add', rev = True)
        def __rsub__(self, other):
            return self.op(other, opkey = 'sub', rev = True)
        def __rmul__(self, other):
            return self.op(other, opkey = 'mul', rev = True)
        def __rmatmul__(self, other):
            return self.op(other, opkey = 'matmul', rev = True)
        def __rtruediv__(self, other):
            return self.op(other, opkey = 'truediv', rev = True)
        def __rfloordiv__(self, other):
            return self.op(other, opkey = 'floordiv', rev = True)
        def __rmod__(self, other):
            return self.op(other, opkey = 'mod', rev = True)
        def __rdivmod__(self, other):
            return self.op(other, opkey = 'divmod', rev = True)
        def __rpow__(self, other):
            return self.op(other, opkey = 'pow', rev = True)
        def __rlshift__(self, other):
            return self.op(other, opkey = 'lshift', rev = True)
        def __rrshift__(self, other):
            return self.op(other, opkey = 'rshift', rev = True)
        def __rand__(self, other):
            return self.op(other, opkey = 'and', rev = True)
        def __rxor__(self, other):
            return self.op(other, opkey = 'xor', rev = True)
        def __ror__(self, other):
            return self.op(other, opkey = 'or', rev = True)

        #### UNARY ####

        def __neg__(self):
            return self.op(opkey = 'neg')
        def __pos__(self):
            return self.op(opkey = 'pos')
        def __abs__(self):
            return self.op(opkey = 'abs')
        def __invert__(self):
            return self.op(opkey = 'invert')
        def __ceil__(self):
            return self.op(opkey = 'ceil')
        def __floor__(self):
            return self.op(opkey = 'floor')
        def __round__(self, ndigits):
            return self.op(opkey = 'round', ndigits = int(ndigits))
        def __trunc__(self):
            return self.op(opkey = 'trunc')
        def __float__(self):
            return self.op(opkey = 'float')
        def __int__(self):
            return self.op(opkey = 'int')
        def __complex__(self):
            return self.op(opkey = 'complex')
        def __str__(self):
            return self.op(opkey = 'str')
        def __index__(self):
            return self.op(opkey = 'index')

        #### BOOLEAN ####

        def __lt__(self, other):
            return self.op(other, opkey = 'lt')
        def __le__(self, other):
            return self.op(other, opkey = 'le')
        def __eq__(self, other):
            return self.op(other, opkey = 'eq')
        def __ne__(self, other):
            return self.op(other, opkey = 'ne')
        def __gt__(self, other):
            return self.op(other, opkey = 'gt')
        def __ge__(self, other):
            return self.op(other, opkey = 'ge')
        def __bool__(self):
            return self.op(opkey = 'bool')
        def __hash__(self):
            return self.op(opkey = 'hash')

        #### CALLS AND RETRIEVALS ####

        def Call(self, args, kwargs) -> 'Function':
            return self._Fn.derived.Call(self.host, args, kwargs)
        def __call__(self, *args, **kwargs) -> 'Function':
            return self.Call(args, kwargs)
        def GetItem(self, arg, /) -> 'Function':
            return self._Fn.derived.GetItem(self.host, arg)
        def __getitem__(self, arg, /) -> 'Function':
            arg = arg if type(arg) is tuple else (arg,)
            arg = arg[0] if len(arg) == 1 else arg
            return self.GetItem(arg)
        def GetAttr(self, arg, /) -> 'Function':
            return self._Fn.derived.GetAttr(self.host, arg)
#         def __getattr__(self, name, /):
#             return self.GetAttr(name)
        def __len__(self):
            return self.op(opkey = 'len')
        def __contains__(self, item):
            return self.op(item, opkey = 'contains')

    @_cached_property
    def v(self):
        return self._V(self)

    #### Deferring methods to v ####

    def __add__(self, other): return self.v + other
    def __sub__(self, other): return self.v - other
    def __mul__(self, other): return self.v * other
    def __matmul__(self, other): return self.v @ other
    def __truediv__(self, other): return self.v / other
    def __floordiv__(self, other): return self.v // other
    def __mod__(self, other): return self.v % other
    def __divmod__(self, other): return self.v.__divmod__(other)
    def __pow__(self, other): return self.v ** other
    def __lshift__(self, other): return self.v << other
    def __rshift__(self, other): return self.v >> other
    def __and__(self, other): return self.v & other
    def __xor__(self, other): return self.v ^ other
    def __or__(self, other): return self.v | other

    #### BINARY REVERSED ####

    def __radd__(self, other): return other + self.v
    def __rsub__(self, other): return other - self.v
    def __rmul__(self, other): return other * self.v
    def __rmatmul__(self, other): return other @ self.v
    def __rtruediv__(self, other): return other / self.v
    def __rfloordiv__(self, other): return other // self.v
    def __rmod__(self, other): return other % self.v
    def __rdivmod__(self, other): return other.__divmod__(self.v)
    def __rpow__(self, other): return other ** self.v
    def __rlshift__(self, other): return other << self.v
    def __rrshift__(self, other): return other >> self.v
    def __rand__(self, other): return other & self.v
    def __rxor__(self, other): return other ^ self.v
    def __ror__(self, other): return other | self.v

    #### UNARY ####

    def __neg__(self): return -self.v
    def __pos__(self): return self.v.__pos__()
    def __abs__(self): return abs(self.v)
    def __invert__(self): return ~self.v
    def __ceil__(self): return self.v.__ceil__()
    def __floor__(self): return self.v.__floor__()
    def __round__(self, ndigits): return self.v.__round__(ndigits)
    def __trunc__(self): return self.v.__trunc__()
    def __float__(self): return self.v.__float__()
    def __int__(self): return self.v.__int__()
    def __complex__(self): return self.v.__complex__()
#     def __str__(self):
#     def __index__(self):

    #### BOOLEAN ####

    def __lt__(self, other): return self.v < other
    def __le__(self, other): return self.v <= other
    def __eq__(self, other): return self.v == other
    def __ne__(self, other): return self.v != other
    def __gt__(self, other): return self.v > other
    def __ge__(self, other): return self.v >= other
#     def __bool__(self): return bool(self.v)
#     def __hash__(self): return hash(self.v)

    #### CALLS AND RETRIEVALS ####

    def __call__(self, *args, **kwargs): return self.v(*args, **kwargs)
    def __getitem__(self, arg): return self.v[arg]
#     def __getattr__(self, name): return self.v.__getattr__(name)
#     def __len__(self):
    def __contains__(self, item): return self.v.__contains__(item)

    ### ITERATION ###

    def __len__(self):
        return len(self.value)
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    ### REPRESENTATIONS ###

    @_cached_property
    def titlestr(self):
        return f"funcy.{self._titlestr()}"
    def _titlestr(self):
        return type(self).__name__
    @_cached_property
    def namestr(self):
        return self._namestr()
    def _namestr(self):
        return self.titlestr + self.kwargstr
    @_cached_property
    def kwargstr(self):
        return self._kwargstr()
    def _kwargstr(self):
        if not len(self.kwargs):
            return ''
        else:
            return _utilities.kwargstr(**self.kwargs)
    @property
    def valstr(self):
        return self._valstr()
    def _valstr(self):
        try:
            return str(self.value)
        except (NullValueDetected, EvaluationError):
            return 'null'
    def __repr__(self):
        return self.namestr
    def __str__(self):
        return self.valstr
    def __format__(self, spec):
        return spec.format(self.__str__())

    @_cached_property
    def hashID(self):
        return self._hashID()
    def _hashID(self):
        return _wordhash.w_hash(repr(self))
    @_cached_property
    def hashInt(self):
        return self._hashInt()
    def _hashInt(self):
        return int(_reseed.digits(12, seed = self.hashID))

    ### RICH COMPARISONS ###

    def __lt__(self, other):
        return hash(self) < hash(other)
    def __le__(self, other):
        return hash(self) <= hash(other)
    def __gt__(self, other):
        return hash(self) > hash(other)
    def __ge__(self, other):
        return hash(self) >= hash(other)
    def __eq__(self, other):
        return hash(self) == hash(other)
    def __ne__(self, other):
        return hash(self) != hash(other)
    def __bool__(self):
        return bool(self.value)
    def __hash__(self):
        return self.hashInt

    ### INDEXING & STORING ###

    @property
    def indices(self):
        try:
            return self._indices
        except AttributeError:
            raise AttributeError("No indices provided.")
    @indices.setter
    def indices(self, indices):
        if hasattr(self, '_indices'):
            self._indices.value = indices
        else:
            self.add_indices(indices)
    def add_indices(self, indices, **kwargs):
        if hasattr(self, '_indices'):
            raise Exception(
                "Function already has indices; remove them with del."
                )
        if isinstance(indices, Function):
            self._indices = Function
        else:
            self._indices = self._Fn(
                dict((v.name, v) for v in map(self._Fn, indices)),
                **kwargs,
                )
    @indices.deleter
    def indices(self):
        del self._indices

    ### DUPLICATION & PICKLING ###

    def copy(self):
        return type(self(*self.terms, **self.kwargs))

    def __reduce__(self):
        return (self._unreduce, (self.terms, self.kwargs))
    @classmethod
    def _unreduce(cls, terms, kwargs):
        return cls._construct(*terms, **kwargs)

###############################################################################
''''''
###############################################################################
