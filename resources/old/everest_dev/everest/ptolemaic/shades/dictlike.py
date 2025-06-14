###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod
from collections.abc import Mapping as _Mapping

from . import _Param

from .shade import Shade as _Shade
from .tuplelike import TupleLike as _TupleLike


class DictLike(_Mapping, _Shade):

    args: _Param.Args

    reqslots = ('dct',)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        if args:
            if kwargs:
                raise RuntimeError(
                    "Cannot input both args and kwargs to DictLike."
                    )
            arg0, *argn = args
            if argn:
                return super().parameterise(arg0, *argn)
            if isinstance(arg0, _Mapping):
                arg0 = arg0.items()
            return super().parameterise(*arg0)
        if kwargs:
            return super().parameterise(*kwargs.items())
        return super().parameterise()

    @classmethod
    def check_param(cls, arg, /):
        if not len(arg) == 2:
            raise ValueError("Input pairs must be of length 2.")
        return super().check_param(arg)

    def __init__(self, /):
        super().__init__()
        self.dct = dict(self.args)

    def __getitem__(self, arg, /):
        return self.dct.__getitem__(arg)

    def __iter__(self, /):
        return iter(self.dct)

    def __len__(self, /):
        return self.dct.__len__()

    def __str__(self, /):
        return ', '.join(map(
            ': '.join,
            zip(map(str, self.keys()), map(str, self.values())),
            ))


###############################################################################
###############################################################################
