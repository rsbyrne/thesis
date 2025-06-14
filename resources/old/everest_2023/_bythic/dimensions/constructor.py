###############################################################################
''''''
###############################################################################

from collections.abc import Iterable as _Iterable

from . import (
    dimension as _dimension,
    collection as _collection,
    multi as _multi,
    range as _range,
    )

def construct(cls, arg):
    if isinstance(arg, tuple):
        return _multi.Multi(*(cls[a] for a in arg))  # pylint: disable=E1136
    # if isinstance(arg, dict):
    #     return _multi.Multi(**{k:cls[v] for k, v in arg.items()})  # pylint: disable=E1136
    # if isinstance(arg, set):
    #     return _multi.Set(*(cls[a] for a in arg))  # pylint: disable=E1136
    if isinstance(arg, slice):
        return _range.Range.construct(arg)
    if isinstance(arg, cls):
        return arg
    if isinstance(arg, _Iterable):
        return _collection.Collection.construct(arg)
    raise TypeError(arg)

_dimension.DimensionMeta.__getitem__ = construct
Dim = _dimension.Dimension

###############################################################################
###############################################################################
