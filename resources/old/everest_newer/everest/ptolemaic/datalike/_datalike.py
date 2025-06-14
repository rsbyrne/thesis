###############################################################################
''''''
###############################################################################


import numpy as _np

from . import _classtools

from . import _Ptolemaic
from . import _ur


class DatalikeMeta(type(_Ptolemaic)):
    @property
    def isur(cls):
        return issubclass(cls, _ur.Ur)
    def get_ur(cls, urcls):
        return getattr(cls, urcls.__name__)


@_classtools.MROClassable
class Datalike(_Ptolemaic, metaclass = DatalikeMeta):

    mroclasses = ('Var', 'Dat', 'Inc', 'Seq', 'Non')

    Var = _ur.Var
    Dat = _ur.Dat
    Inc = _ur.Inc
    Seq = _ur.Seq
    Non = _ur.Non

    dtype = _np.generic

    @classmethod
    def _process_dtype(cls, dtype):
        dtype = type(dtype) if not isinstance(dtype, type) else dtype
        if not issubclass(dtype, _np.generic):
            dtype = getattr(_np, f"{dtype.__name__}_")
        if not dtype is (deftype := cls.dtype):
            if not issubclass(dtype, deftype):
                raise ValueError(
                    f"Input dtype {dtype}"
                    f"is not a subclass of default dtype {deftype}"
                    f"on class {cls}"
                    )
        return dtype

    def __init__(self, *args, dtype = None, **kwargs):
        if not dtype is None:
            if not dtype is self.dtype:
                self.dtype = dtype
                self.register_argskwargs(dtype = dtype)  # pylint: disable=E1101
        super().__init__(*args, **kwargs)


###############################################################################
###############################################################################
