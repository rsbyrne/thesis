###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools
import hashlib as _hashlib
import itertools as _itertools
from collections import abc as _collabc

import more_itertools as _mitertools

from . import _utilities

_caching = _utilities.caching
_word = _utilities.word


def get_hintstr(hint):
    if isinstance(hint, tuple):
        return f"({', '.join(map(get_hintstr, hint))})"
    if isinstance(hint, type):
        return hint.__name__
    return repr(hint)


def get_hint(hints):
    nhints = len(hints)
    if nhints:
        if nhints == 1:
            return hints[0]
        return hints
    return _inspect._empty


def sort_params(params, /):
    params = sorted(params, key=(lambda x: x.default is not _inspect._empty))
    params = sorted(params, key=(lambda x: x.kind))
    return params


class ParamMeta(type):

    _kinds = dict(zip(
        _inspect._ParameterKind,
        ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs')
        ))
    _revkinds = dict(zip(_kinds.values(), _kinds.keys()))
    _defaultkind = _inspect._ParameterKind.POSITIONAL_OR_KEYWORD

    def __new__(meta,
            name, bases, namespace,
            kind=None,
            hint=_inspect._empty,
            **kwargs
            ):

        bases = tuple(_mitertools.unique_everseen(bases))

        if isinstance(kind, str):
            kind = meta._revkinds[kind]
        bks = (base.kind for base in bases if isinstance(base, meta))
        kinds = (*bks, kind)
        kinds = tuple(set(kind for kind in kinds if kind is not None))
        nkinds = len(kinds)
        if nkinds:
            if nkinds > 1:
                raise TypeError
            kind = kinds[0]
        else:
            kind = None
        kindstr = meta._kinds[meta._defaultkind if kind is None else kind]

        bhs = (base.hints for base in reversed(bases) if isinstance(base, meta))
        hints = (*_itertools.chain.from_iterable(bhs), hint)
        hints = tuple(hint for hint in hints if hint is not _inspect._empty)
        hintstr = get_hintstr(hints)[1:-1]

        namespace.update(
            hints=hints,
            hint=get_hint(hints),
            kind=kind,
            _rootname=name,
            )

        name += f".{kindstr}"
        if hintstr:
            name += f"[{hintstr}]"

        return super().__new__(meta, name, bases, namespace, **kwargs)

    def __getitem__(cls, arg, /):
        if arg is cls:
            return cls
        if isinstance(arg, type(cls)):
            return type(cls)(arg._rootname, (cls, arg), {}, kind=arg.kind)
        return type(cls)(cls._rootname, (cls,), {}, hint=arg, kind=cls.kind)


class Param(metaclass=ParamMeta):

    __slots__ = ('name', 'default', 'parameter',)

    def __init__(self, name, default=_inspect.Parameter.empty, /):
        self.name, self.default = name, default
        kind = self.kind
        if kind is None:
            kind = type(self)._defaultkind
        self.parameter = _inspect.Parameter(
            name, kind, default=default, annotation=self.hint,
            )

    def __get__(self, instance, /, owner=None):
        return getattr(instance.params, self.name)

    def _repr(self):
        return f"name={self.name}, default={self.default}"

    def __repr__(self):
        return f"{type(self).__name__}({self._repr()})"


for name in Param._revkinds:
    subcls = type(Param)(Param._rootname, (Param,), {}, kind=name)
    setattr(Param, name, subcls)


Param = Param.PosKw


class Params(_collabc.Mapping):

    __slots__ = ('bound', 'arguments', '_getter', '_softcache')

    def parameterise(self, /, *args, **kwargs):
        return args, kwargs

    signed = False

    def __init__(self, /, *args, **kwargs):
        args, kwargs = self.parameterise(*args, **kwargs)
        bound = self.bound = self.sig.bind(*args, **kwargs)
        bound.apply_defaults()
        self.arguments = bound.arguments

    def __getattr__(self, name):
        if name in (arguments := self.arguments):
            return arguments[name]
        return super().__getattr__(name)

    @_caching.soft_cache(None)
    def __str__(self):
        args = self.arguments
        return ', '.join(map('='.join, zip(args, map(repr, args.values()))))

    @_caching.soft_cache(None)
    def __repr__(self):
        return f"{type(self).__name__}({self.__str__()})"

    @property
    @_caching.soft_cache(None)
    def hashcode(self):
        content = str(self).encode()
        return _hashlib.md5(content).hexdigest()

    @property
    @_caching.soft_cache(None)
    def hashint(self):
        return int(self.hashcode, 16)

    @property
    @_caching.soft_cache(None)
    def hashID(self):
        return _word.get_random_english(seed=self.hashint, n=2)

    def __getitem__(self, arg, /):
        return self.arguments[arg]

    def __iter__(self, /):
        return iter(self.arguments)

    def __len__(self, /):
        return len(self.arguments)

    @classmethod
    def __init_subclass__(cls, /, *, sig, parameterise, **kwargs):
        if cls.signed:
            raise TypeError(f"{type(cls)} already signed.")
        cls.sig = sig
        cls.parameterise = parameterise
        cls.signed = True
        super().__init_subclass__(**kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return type(cls)(
            f"{cls.__name__}[{repr(arg)}]",
            (cls,),
            dict(),
            sig=arg.__signature__,
            parameterise=arg.parameterise,
            )


###############################################################################
###############################################################################
