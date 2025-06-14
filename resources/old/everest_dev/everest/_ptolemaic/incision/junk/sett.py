###############################################################################
''''''
###############################################################################


import functools as _functools
import collections.abc as _collabc

from . import _utilities

from .sliceable import Sliceable as _Sliceable


def always_true(arg):
    return True


class Sett(_Sliceable):

    @classmethod
    def parameterise(cls, register, /, *criteria, **kwargs):
        register(*criteria)
        super().parameterise(register, **kwargs)

    def __init__(self, criteria0=always_true, /, *criteria):
        criteria = self.criteria = (criteria0, *criteria)
        self.criterion_function = \
            _utilities.process_criterion([super().__contains__, *criteria])
        super().__init__()

    @property
    def __contains__(self):
        return self.criterion_function

    def incise_sampler(self, sampler):
        return self.new_self(*self.criteria, sampler)

    @classmethod
    def slice_methods(cls, /):
        yield (type(None), type(None), _collabc.Callable), cls.incise_sampler
        yield from super().slice_methods()


###############################################################################
###############################################################################
