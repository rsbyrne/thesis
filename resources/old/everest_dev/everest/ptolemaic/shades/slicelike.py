###############################################################################
''''''
###############################################################################


from . import _Param

from .shade import Shade as _Shade


class SliceLike(_Shade):

    start: _Param.Pos = None
    stop: _Param.Pos = None
    step: _Param.Pos = None

    reqslots = ('slc',)

    @classmethod
    def parameterise(self, arg0, /, *argn):
        if not argn:
            if isinstance(arg0, slice):
                return super().parameterise(arg0.start, arg0.stop, arg0.step)
            return super().parameterise(None, arg0)
        return super().parameterise(arg0, *argn)

    def __init__(self, /):
        super().__init__()
        self.slc = slice(self.start, self.stop, self.step)

    def __str__(self, /):
        return ': '.join(map(str, (self.params.values())))


###############################################################################
###############################################################################
