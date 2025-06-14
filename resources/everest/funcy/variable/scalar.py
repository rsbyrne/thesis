from numbers import Real, Integral

from .number import Number
from ..special import null
from .exceptions import *

class Scalar(Number):

    __slots__ = (
        'memory',
        '_prev',
        'stack',
        '_rectified',
        )

    def __init__(self,
            arg = None,
            /,
            *args,
            dtype = None,
            **kwargs,
            ):
        if type(arg) is type:
            if not dtype is None:
                raise TypeError(
                    "Cannot provide both kwarg 'dtype' and arg of type 'type'"
                    )
            if issubclass(arg, Real):
                dtype = arg
            else:
                raise TypeError(arg)
            initVal = null
        elif isinstance(arg, Real):
            dtype = type(arg) if dtype is None else dtype
            initVal = arg
        elif arg is None:
            if dtype is None:
                raise ValueError("Insufficient inputs.")
            initVal = null
        else:
            raise TypeError(type(arg))
        super().__init__(
            tuple(),
            dtype,
            *args,
            _initVal = initVal,
            **kwargs
            )
        self._rectified = False
        def rectify():
            if not self._rectified:
                try:
                    self.memory = self.dtype(self.memory)
                    self._rectified = True
                except TypeError:
                    if self.memory is Ellipsis:
                        self.memory = self._prev
                        self._rectified = True
                    if self.memory is null:
                        raise NullValueDetected
                    elif hasattr(self.memory, '_funcy_setvariable__'):
                        self.memory._funcy_setvariable__(self)
                        self.rectify()
                    else:
                        self.nullify()
                        raise TypeError(self.memory)
        self.rectify = rectify

    def set_value(self, val):
        self._prev = self.memory
        self.memory = val
        self._rectified = False
