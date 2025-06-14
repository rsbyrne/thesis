###############################################################################
''''''
###############################################################################


from collections.abc import Iterable as _Iterable, Sequence as _Sequence

from . import _Param

from .shade import Shade as _Shade


class TupleLike(_Sequence, _Shade):

    args: _Param.Args

    reqslots = ('typ', '_len',)

    @classmethod
    def parameterise(cls, arg, /, *args):
        if args:
            return super().parameterise(arg, *args)
        if isinstance(arg, _Iterable):
            return super().parameterise(*arg)
        return super().parameterise(arg)     

    def __init__(self, /):
        super().__init__()
        args = self.args
        self._len = len(args)
        typs = set(map(type, args))
        if len(typs) == 1:
            self.typ = typs.pop()
        else:
            self.typ = None

    def __getitem__(self, arg, /):
        return self.args.__getitem__(arg)

    def __iter__(self, /):
        return iter(self.args)

    def __len__(self, /):
        return self._len

    def __str__(self, /):
        return ', '.join(map(str, self.args))


###############################################################################
###############################################################################
