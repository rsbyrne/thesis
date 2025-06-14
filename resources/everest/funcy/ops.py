from collections.abc import Mapping
from collections import OrderedDict
from functools import cached_property, lru_cache, wraps, partial
import inspect

def op_wrap(func, *keys, opclass):
    @wraps(func)
    def subwrap(*args, **kwargs):
        return func(*args, **kwargs)
    subwrap.__name__ = '.'.join([
        *(k for k in keys if not k.startswith('_')),
        func.__name__,
        ])
    @wraps(func)
    def wrapper(*args, **kwargs):
        return opclass(
            *args,
            op = subwrap,
            **kwargs
            )
    return wrapper

class Ops:
    __slots__ = (
        'source',
        'rawsource',
        'keys',
        'opclass',
        '_sourceType'
        )
    def __init__(self, source, *keys, opclass):
        self.rawsource = source
        self.opclass = opclass
        if inspect.ismodule(source):
            self.source = source
            self._sourceType = 'module'
        elif inspect.isclass(source):
            self.source = source
            self._sourceType = 'class'
        elif isinstance(source, Mapping):
            self.source = OrderedDict()
            self._sourceType = 'mapping'
            for k, v in source.items():
                if any([
                        isinstance(v, Mapping),
                        inspect.ismodule(v),
                        inspect.isclass(v)
                        ]):
                    self.source[k] = Ops(
                        v,
                        *(*keys, k),
                        opclass = self.opclass,
                        )
                elif callable(v):
                    self.source[k] = v
                else:
                    raise TypeError(v, type(v))
        else:
            raise TypeError(source, type(source))
        self.keys = keys
    @lru_cache
    def __getitem__(self, key):
        got = self.getfn(key)
        if type(got) is Ops:
            return got
        else:
            return op_wrap(
                got,
                *self.keys,
                opclass = self.opclass
                )
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError
    @lru_cache
    def getfn(self, key):
        if type(key) is tuple:
            targ = self
            for k in key:
                targ = targ[k]
            return targ
        else:
            try:
                if self._sourceType in {'module', 'class'}:
                    try:
                        obj = getattr(self.source, key)
                    except AttributeError:
                        raise KeyError
                elif self._sourceType == 'mapping':
                    obj = self.source[key]
                else:
                    raise ValueError("Sourcetype was:", self._sourceType)
                return obj
            except KeyError:
                if self._sourceType == 'mapping':
                    for v in self.source.values():
                        if type(v) is Ops:
                            try:
                                return v.getfn(key)
                            except KeyError:
                                pass
                    raise KeyError
                else:
                    raise KeyError

    def __call__(self, key, *args, **kwargs):
        return self[key](*args, **kwargs)

def getitem(x, y):
    return x[y]
def call(x, y):
    return x(y)
def amp(x, y):
    return x and y
def bar(x, y):
    return x or y
def hat(x, y):
    return (x or y) and not (x and y)
# def exc(x, e, y):
#     t

import math
import builtins
import operator
import itertools
import numpy
import scipy
import sklearn
from everest import reseed
from . import operations
from .seq import seqoperations
sources = OrderedDict(
    _op = operations,
    _sop = seqoperations,
    _basic = dict(
        getitem = getitem,
        call = call,
        amp = amp,
        bar = bar,
        hat = hat,
        ),
    _builtins = builtins,
    _operator = operator,
    _math = math,
    _itertools = itertools,
    rs = reseed.Reseed,
    np = numpy,
    sp = scipy,
    sk = sklearn,
    )

from .operation import Operation
from .seq.seqoperation import SeqOperation
ops = Ops(sources, opclass = Operation)
seqops = Ops(sources, opclass = SeqOperation)
