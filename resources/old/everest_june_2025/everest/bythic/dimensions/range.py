###############################################################################
''''''
###############################################################################

from functools import partial as _partial

from . import _special, _reseed #_classtools

from .countable import Countable as _Countable
from .utilities import unpack_slice

class Range(_Countable):

    __slots__ = ('slc', 'start', 'stop', 'step', 'startinf', 'stopinf')
    Inf, inf, ninf = (_special.Infinite, None, None,)

    @classmethod
    def proc_arg(cls, arg, step, inv = False):
        if arg is None:
            if inv:
                lower, upper = cls.inf, cls.ninf
            else:
                lower, upper = cls.ninf, cls.inf
            return lower if step > 0 else upper
        if isinstance(arg, cls.Inf):
            return arg
        return cls.typ(arg) # pylint: disable=E1102

    @classmethod
    def construct(cls, *args):
        _, *args = unpack_slice(*args)
        if cls is Range:
            start, stop, step = args
            if isinstance(step, float):
                return Real(*args)
            if isinstance(step, int):
                return Integral(*args)
            if any(
                    isinstance(st, (cls.Inf, type(None)))
                        for st in (start, stop)
                    ):
                raise ValueError(
                    "Cannot have an open range with a non-finite step"
                    )
            if any(isinstance(st, float) for st in (start, stop)):
                return Real(*args)
            return Integral(*args)
        return cls(*args) # pylint: disable=E1120

    @classmethod
    def proc_args(cls, start, stop, step, stepdefault = 1):
        step = stepdefault if step is None else step
        if isinstance(step, cls.typ):
            start = cls.proc_arg(start, step)
            stop = cls.proc_arg(stop, step, inv = True)
            if any((
                    (step > 0 and start > stop),
                    (step < 0 and start < stop),
                    start == stop
                    )):
                raise ValueError("Zero-length range.")
            return start, stop, step
        return cls.typ(start), cls.typ(stop), step # pylint: disable=E1102

    @classmethod
    def analyse_range_args(cls, arg0, arg1 = None, arg2 = None):
        slc, *args = unpack_slice(arg0, arg1, arg2)
        start, stop, step = cls.proc_args(*args)
        startinf, stopinf = (isinstance(st, cls.Inf) for st in (start, stop))
        return slc, start, stop, step, startinf, stopinf

    def __init__(self, slc, start, stop, step, startinf, stopinf, /, **kwargs):
        self.slc = slc
        self.start, self.stop, self.step = start, stop, step
        self.startinf, self.stopinf = startinf, stopinf
        super().__init__(**kwargs)
        self.register_argskwargs(start, stop, step) # pylint: disable=E1101


class Integral(Range):

    Inf, inf, ninf, typ = \
        _special.InfiniteInteger, _special.infint, _special.ninfint, int

    def __init__(self, *args, **kwargs):
        slc, start, stop, step, startinf, stopinf = self.analyse_range_args(
            *args
            )
        if isinstance(step, str):
            choices = list(range(start, stop))
            _reseed.rshuffle(choices, seed = step)
            self.iter_fn = choices.__iter__
            self.iterlen = len(choices)
        elif not startinf:
            rang = self.rang = range(start, stop, step)
            self.iter_fn = rang.__iter__
            if not stopinf:
                self.iterlen = len(rang)
        super().__init__(slc, start, stop, step, startinf, stopinf, **kwargs)

    def indices(self, n):
        return self.slc.indices(n)


def real_range(incrementer, stop, step):
    while incrementer < stop:
        yield round(incrementer, 12)
        incrementer += step

def rand_float_range(start, stop, seed):
    rsd = _reseed.Reseed(seed)
    while True:
        yield round(rsd.rfloat(start, stop), 12)

class Real(Range):

    Inf, inf, ninf, typ = \
        _special.InfiniteFloat, _special.infflt, _special.ninfflt, float

    def __init__(self, *args, **kwargs):
        slc, start, stop, step, startinf, stopinf = self.analyse_range_args(
            *args
            )
        if isinstance(step, str):
            self.iter_fn = _partial(rand_float_range, start, stop, step)
            self.iterlen = _special.infint
        elif not startinf:
            self.iter_fn = _partial(real_range, start, stop, step)
            if not stopinf:
                self.iterlen = int(abs(stop - start) // step) + 1
        super().__init__(slc, start, stop, step, startinf, stopinf, **kwargs)

###############################################################################
###############################################################################
