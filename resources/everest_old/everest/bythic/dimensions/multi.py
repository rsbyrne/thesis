###############################################################################
''''''
###############################################################################

import itertools as _itertools
from functools import partial as _partial, reduce as _reduce
import operator as _operator
from collections.abc import Iterable as _Iterable

from . import _special, _everestutilities

from .dimension import Dimension as _Dimension
from .range import Range as _Range
from .collection import Collection as _Collection

_muddle = _everestutilities.seqmerge.muddle

def process_depth(
        args: tuple, depth: int, /,
        filler = NotImplemented,
        ):
    if not args:
        return args
    args = tuple(arg if arg != slice(None) else filler for arg in args)
    if (not depth < _special.infint) and (Ellipsis in args):
        raise ValueError("Cannot use ellipsis when depth is infinite.")
    nargs = len(args)
    if nargs == 0:
        return args
    if nargs == 1:
        if args[0] is Ellipsis:
            return tuple(filler for _ in range(depth))
        return args
    if nargs < depth:
        nellipses = len(tuple(el for el in args if el is Ellipsis))
        if nellipses == 0:
            return args
        if nellipses == 1:
            out = []
            for arg in args:
                if arg is Ellipsis:
                    for _ in range(depth + 1 - nargs):
                        out.append(filler)
                else:
                    out.append(arg)
            return tuple(out)
        raise IndexError(f"Too many ellipses ({nellipses} > 1)")
    if nargs == depth:
        return tuple(filler if arg is Ellipsis else arg for arg in args)
    raise IndexError(
        f"Not enough depth to accommodate requested levels:"
        f" levels = {nargs} > depth = {depth})"
        )

def incise_dims(args, dims, collapsed):
    args = iter(args)
    for dim, coll in zip(dims, collapsed):
        if coll:
            yield dim
        else:
            try:
                yield dim[next(args)]
            except StopIteration:
                yield dim
    yield from args

def is_collapsed(dim):
    if isinstance(dim, _Dimension):
        return dim.collapsed
    return True


class Multi(_Dimension):

    def __init__(self, *dims):
        dims = tuple(self.process_dims(dims))
        self.dims = dims
        self.depth = len(dims)
        collapsed = self.collapsed = tuple(is_collapsed(dim) for dim in dims)
        self.activedepth = collapsed.count(False)
        super().__init__()
        self.register_argskwargs(*dims) # pylint: disable=E1101

    def iter_fn(self):
        try:
            iter_fn = self._iter_fn
        except AttributeError:
            dims = self.dims
            if all(dim.tractable for dim in dims):
                iter_fn = _partial(_itertools.product, *dims)
            else:
                iter_fn = _partial(_muddle, dims)
            self._iter_fn = iter_fn # pylint: disable=W0201
        return iter_fn()
    def calculate_len(self):
        return _reduce(_operator.mul, (dim.iterlen for dim in self.dims), 1)

    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        activedepth = self.activedepth
        if len(args) <= activedepth:
            args = process_depth(args, activedepth)
        return type(self)(*incise_dims(args, self.dims, self.collapsed))

    def get_valstr(self):
        return str([repr(dim) for dim in self.dims])

    @classmethod
    def process_dims(cls, dims):
        for dim in dims:
            if isinstance(dim, _Dimension):
                yield dim
            elif isinstance(dim, slice):
                yield _Range.construct(dim)
            elif isinstance(dim, _Iterable):
                yield _Collection.construct(dim)
            else:
                yield dim

###############################################################################
###############################################################################
