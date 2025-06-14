###############################################################################
'''The module that defines the Incision Protocol.'''
###############################################################################

import itertools as _itertools
from functools import reduce as _reduce
from operator import mul as _mul

from . import _special, _seqmerge, _abstract, _mroclasses
from .incisable import SoftIncisable as _SoftIncisable
from . import incisor as _incisor

@_mroclasses.Overclass
class Incision:
    def __init__(self, source, *args, **kwargs):
        self._source = source
        super().__init__(*args, **kwargs)
    @property
    def source(self):
        return self._source
    @property
    def levelsource(self):
        if hasattr(src := self.source, 'levelsource'):
            return src.levelsource
        return src
    @property
    def truesource(self):
        if hasattr(src := self.source, 'truesource'):
            return src.truesource
        return src
    @property
    def mimicsource(self):
        return self.levelsource
    def levels(self):
        yield from self.source.levels()
    @property
    def depth(self):
        return self.source.depth
    def __call__(self, *args, **kwargs):
        return self.truesource(*args, **kwargs)
    @_mroclasses.AnticipatedMethod
    def __getitem__(self, arg):
        '''Should be overridden by Incisable.__getitem__'''

class DeepIncision(Incision):
    @classmethod
    def process_depth(cls,
            args: tuple, depth: int, /,
            filler = _incisor.trivial,
            ):
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
                        for _ in range(depth - nargs):
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
    def __init__(self, args, source):
        if args is Ellipsis:
            args = (Ellipsis,)
        nargs = len(args)
        if nargs == 0:
            raise ValueError("Cannot process empty tuple.")
        args = self.process_depth(args, source.depth)
        if (nargs := len(args)) < (nlevels := source.nlevels):
            args = tuple((
                *args, *(_incisor.trivial for _ in range(nlevels - nargs))
                ))
        argiter, levels = iter(args), source.levels()
        cursor = next(levels)[next(argiter)]
        for arg, lev in _itertools.zip_longest(argiter, levels):
            cursor = cursor[_incisor.subinc]
            if hasattr(lev, 'incisors'):
                for inc in lev.incisors:
                    cursor = cursor[inc]
            cursor = cursor[arg]
        super().__init__(cursor)
    def levels(self):
        return self.source.levels()
    @property
    def length(self):
        return _reduce(_mul, (lev.length for lev in self.levels()), 1)
    def __getitem__(self, arg, /):
        if not isinstance(arg, tuple):
            arg = (arg,)
        return super().__getitem__(arg)
    def indices(self):
        return _seqmerge.muddle((
            level.indices() for level in self.levels()
            ))
    def __iter__(self):
        return (self(*inds) for inds in self.indices())

class SubIncision(Incision):
    def __init__(self, _, source):
        super().__init__(source, **source.subkwargs)
    @property
    def levelsource(self):
        return self
    @property
    def mimicsource(self):
        if isinstance(src := self.source, Incision):
            return src.levelsource
        return src
    def levels(self):
        yield from super().levels()
        yield self
    @property
    def depth(self):
        return super().depth - 1
    def get_incision_method(self, arg, /):
        return self.mimicsource.get_incision_method(arg)

class ShallowIncision(Incision, _SoftIncisable):
    def __init__(self, incisor, /, *args, **kwargs):
        self.incisor = incisor
        super().__init__(*args, **kwargs)
    @property
    def subkwargs(self):
        return self.levelsource.subkwargs
    @property
    def _sourceincisors(self):
        if isinstance(src := self.source, ShallowIncision):
            return src.incisors
        return ()
    @property
    def incisors(self):
        yield from self._sourceincisors
        yield self.incisor
    def levels(self):
        *levels, _ = super().levels()
        yield from levels
        yield self
    def get_incision_method(self, arg, /):
        meth = self.source.get_incision_method(arg)
        if meth is NotImplemented:
            return super().get_incision_method(arg)
        return meth

class StrictIncision(ShallowIncision):
    _length = 1
    def indices(self):
        yield self.incisor

class BroadIncision(ShallowIncision):
    def __init__(self, incisor, /, *args, **kwargs):
        super().__init__(incisor, *args, lev = len(incisor), **kwargs)
    def index_sets(self):
        yield self.incisor
        yield from super().index_sets()
    def index_types(self):
        yield object
        yield from super().index_types()

class SoftIncision(ShallowIncision):

    _length = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iter_fn = self._get_iter_fn()
    def _indices_getslice(self):
        inc, src = self.incisor, self.source
        return _itertools.islice(
            src.allindices(),
            inc.start, inc.stop, inc.step
            )
    def _indices_getinterval(self):
        inc, src = self.incisor, self.source
        start, stop, step = inc.start, inc.stop, inc.step
        start = 0 if start is None else start
        stop = _special.infint if stop is None else stop
        starti, stopi, stepi = (src.get_indi(s) for s in (start, stop, step))
        itr = src.allindices()
        started = False
        stopped = False
        try:
            while not started:
                inds = next(itr)
                started = inds[starti] >= start
            if step is None:
                inner_loop = lambda _: next(itr)
            else:
                def inner_loop(inds):
                    stepped = False
                    thresh = inds[stepi] + step
                    while not stepped:
                        inds = next(itr)
                        stepped = inds[stepi] >= thresh
                    return inds
            while not stopped:
                yield inds
                inds = inner_loop(inds)
                stopped = inds[stopi] >= stop
        except StopIteration:
            pass
    def _indices_getkeys(self):
        inc, src = self.incisor, self.source
        for i, inds in _seqmerge.muddle((inc, src.allindices())):
            if i == inds[src.get_indi(i)]:
                yield inds
    def _indices_getmask(self):
        inc, src = self.incisor, self.source
        for mask, inds in zip(inc, src.allindices()):
            if mask:
                yield inds
    def _get_iter_fn(self):
        incisor = self.incisor
        if isinstance(incisor, _abstract.general.Slice):
            _ss = incisor.start, incisor.stop, incisor.step
            if all(
                    isinstance(s, (
                            _abstract.general.NoneType,
                            _abstract.datalike.Integral
                            ))
                        for s in _ss
                    ):
                return self._indices_getslice
            return self._indices_getinterval
        if isinstance(incisor, _abstract.structures.Iterable):
            if all(isinstance(i, _abstract.datalike.Bool) for i in incisor):
                return self._indices_getmask
            return self._indices_getkeys
        raise TypeError(incisor, type(incisor))
    def index_sets(self):
        return zip(*(
            (*srcinds, *slfinds)
                for srcinds, slfinds in zip(
                    self.iter_fn(),
                    zip(*super().index_sets()),
                    )
            ))
    def index_types(self):
        yield from self.source.index_types()
        yield from super().index_types()

###############################################################################
###############################################################################
