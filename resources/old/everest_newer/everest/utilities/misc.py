###############################################################################
'''Generally useful code snippets for funcy.'''
###############################################################################


from abc import ABC as _ABC
from collections import abc as _collabc
import collections as _collections
import itertools as _itertools
import os as _os
import random as _random
from functools import lru_cache as _lru_cache

import numpy as _np


RICHOPS = ('lt', 'le', 'eq', 'ne', 'ge', 'gt')
BOOLOPS = ('not', 'truth', 'is', 'is_not',)
ARITHMOPS = (
    'abs', 'add', 'and', 'floordiv', 'index', 'inv',
    'lshift', 'mod', 'mul', 'matmul', 'neg', 'or',
    'pos', 'pow', 'rshift', 'sub', 'truediv', 'xor'
    )
REVOPS = (
    'radd', 'rand', 'rfloordiv', 'rlshift', 'rmod', 'rmul',
    'rmatmul', 'ror', 'rpow', 'rrshift', 'rsub', 'rtruediv',
    'rxor',
    )
SEQOPS = ('concat', 'contains', 'countOf', 'indexOf', )
ALLOPS = (*RICHOPS, *BOOLOPS, *ARITHMOPS, *SEQOPS)


def unpackable(obj):
    return all(
        isinstance(obj, _collabc.Iterable),
        not isinstance(obj, _collabc.Collection),
        )


def unpacker_zip(arg1, arg2, /):
    arg1map, arg2map = (
        isinstance(arg, _collabc.Mapping)
            for arg in (arg1, arg2)
        )
    if arg1map and arg2map:
        arg1, arg2 = zip(*((arg1[k], arg2[k]) for k in arg1 if k in arg2))
        arg1, arg2 = iter(arg1), iter(arg2)
    elif arg1map:
        arg1 = arg1.values()
    elif arg2map:
        arg2 = arg2.values()
    if unpackable(arg1):
        if not unpackable(arg2):
            arg2 = _itertools.repeat(arg2)
        for sub1, sub2 in zip(arg1, arg2):
            yield from unpacker_zip(sub1, sub2)
    else:
        yield arg1, arg2

def kwargstr(**kwargs):
    outs = []
    for key, val in sorted(kwargs.items()):
        if not type(val) is str:
            try:
                val = val.namestr
            except AttributeError:
                try:
                    val = val.__name__
                except AttributeError:
                    val = str(val)
        outs.append(': '.join((key, val)))
    return '{' + ', '.join(outs) + '}'

def process_scalar(scal):
    return scal.dtype.type(scal)

def add_headers(path, header = '#' * 80, footer = '#' * 80, ext = '.py'):
    path = _os.path.abspath(path)
    for filename in _os.listdir(path):
        subPath = _os.path.join(path, filename)
        if _os.path.isdir(subPath):
            add_headers(subPath)
        filename, extension = _os.path.splitext(filename)
        if extension == ext:
            with open(subPath, mode = 'r+') as file:
                content = file.read()
                file.seek(0, 0)
                if not content.strip('\n').startswith(header):
                    content = f"{header}\n\n{content}"
                if not content.strip('\n').endswith(footer):
                    content = f"{content}\n\n{footer}\n"
                file.write(content)


class FrozenMap(_collections.UserDict):

    lock = False

    def __init__(self, *args, defertos = (), **kwargs):
        super().__init__(*args, **kwargs)
        self.defertos = tuple(defertos)
        self.lock = True

    def __setitem__(self, name, value):
        if self.lock:
            raise ValueError(f"Cannot set value on {type(self)}")
        super().__setitem__(name, value)

    def __delitem__(self, name):
        if self.lock:
            raise ValueError(f"Cannot delete value on {type(self)}")
        super().__delitem__(name)

    def __getitem__(self, name):
        try:
            return super().__getitem__(name)
        except KeyError:
            return self._getitem_deferred(name)

    def getitem_deferred(self, key):
        for deferto in self.defertos:
            try:
                return deferto[key]
            except KeyError:
                continue
        raise KeyError(key)

    def __repr__(self):
        return f"{type(self).__name__}(len=={len(self)})"

    def __hash__(self):
        try:
            return self._hashint
        except AttributeError:
            hashint = self._hashint = _random.randint(
                int(1e12),
                int(1e13) - 1
                )
            return hashint


class FrozenOrderedMap(FrozenMap, _collections.OrderedDict):
    ...


class TypeMap(FrozenOrderedMap):

    @_lru_cache
    def __getitem__(self, key):
        keys = tuple(iter(self))
        vals = (super(type(self), self).__getitem__(k) for k in keys)
        for compkey, arg in zip(keys, vals):
            if issubclass(key, compkey):
                return arg
        return self.getitem_deferred(key)


class SliceLike(_ABC):
    ...
_ = SliceLike.register(slice)

class Slyce:

    __slots__ = (
        'start', 'stop', 'step',
        'slc', 'args', 'hasargs',
        )

    def __init__(self, start = None, stop = None, step = None, /):
        args = self.args = self.start, self.stop, self.step = \
            start, stop, step
        self.hasargs = tuple(x is not None for x in args)
        self.slc = slice(start, stop, step)

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return 3

    def __getitem__(self, arg):
        return self.args[arg]

    def __repr__(self):
        return f"Slyce({self.start}, {self.stop}, {self.step})"

_ = SliceLike.register(Slyce)

def slyce(arg, *args):
    if isinstance(arg, slice) and not args:
        return Slyce(arg.start, arg.stop, arg.step)
    return Slyce(arg, *args)

# def delim_split(seq, /, sep = ...):
#     g = []
#     for el in seq:
#         if el == sep:
#             if g:
#                 if not (len(g) == 1 and g[0] == sep):
#                     yield tuple(g)
#             g.clear()
#         g.append(el)
#     if g:
#         if not (len(g) == 1 and g[0] == sep):
#             yield tuple(g)

###############################################################################
###############################################################################
