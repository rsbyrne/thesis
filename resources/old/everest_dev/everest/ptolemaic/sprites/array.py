###############################################################################
''''''
###############################################################################


from collections.abc import Iterable as _Iterable

import numpy as _np

from . import _Param

from .sprite import Sprite as _Sprite


class Array(_Sprite):

    inbytes: _Param.Pos[bytes]
    dtype: _Param.Kw[str]

    reqslots = ('_arr',)

    @classmethod
    def parameterise(cls, arg, /, *, dtype=None):
        if isinstance(arg, bytes):
            return super().parameterise(bytes(arg), dtype=str(dtype))
        arg = _np.array(arg)
        if not dtype is None:
            arg = arg.astype(dtype)
        inbuff = bytes(arg)
        dtype = arg.dtype
        return super().parameterise(inbuff, dtype=str(dtype))

    def __init__(self, /):
        arr = self._arr = _np.frombuffer(self.inbytes, dtype=self.dtype)
        arr.setflags(write=False)

    @property
    def arr(self, /):
        return self._arr

    @property
    def shape(self, /):
        return self._arr.shape

    @property
    def dtype(self, /):
        return self._arr.dtype

    def __getitem__(self, arg, /):
        return self._arr.__getitem__(arg)

    def __iter__(self, /):
        return self._arr.__iter__()

    def __len__(self, /):
        return self._arr.__len__()

    def __str__(self, /):
        return self._arr.__str__()


###############################################################################
###############################################################################
