###############################################################################
''''''
###############################################################################

from numbers import Real as _Real, Integral as _Integral
from typing import Optional as _Optional, Union as _Union

from . import _generic
from .numerical import (
    Numerical as _Numerical,
    NumericalConstructFailure,
    )

from .exceptions import *

class ScalarConstructFailure(NumericalConstructFailure):
    ...

class Scalar(_Numerical, _generic.Number):

    __slots__ = (
        'memory',
        '_prev',
        'stack',
        '_rectified',
        )

    @classmethod
    def _construct(cls,
            arg: _Optional[_Union[type, _Real]] = None,
            /, *args, **kwargs
            ) -> _Numerical:
        if len(args):
            raise ScalarConstructFailure(
                "Cannot pass multiple args to scalar constructor"
                )
        kwargs = kwargs.copy()
        if not arg is None:
            if (argType := type(arg)) is type or argType is str:
                if 'dtype' in kwargs:
                    raise ScalarConstructFailure(
                        "Cannot provide both arg-as-dtype and dtype kwarg"
                        " to scalar constructor"
                        )
                kwargs['dtype'] = arg
            else:
                if 'initVal' in kwargs:
                    raise ScalarConstructFailure(
                        "Cannot provide both arg-as-initVal"
                        " and 'initVal' kwarg to scalar constructor."
                        )
                kwargs['initVal'] = arg
                if not 'dtype' in kwargs:
                    kwargs['dtype'] = type(arg)
        try:
            dtype = kwargs['dtype']
        except KeyError:
            raise ScalarConstructFailure(
                "No 'dtype' kwarg or arg interpretable as a datatype"
                " was provided to scalar constructor."
                )
        try:
            dtype = cls._check_dtype(dtype)
        except TypeError as e:
            raise ScalarConstructFailure(e)
        if issubclass(dtype, _Real):
            if cls in {Scalar, ScalarIntegral, ScalarReal}:
                try:
                    if issubclass(dtype, _Integral):
                        return ScalarIntegral(**kwargs)
                    else:
                        return ScalarReal(**kwargs)
                except Exception as e:
                    raise ScalarConstructFailure(
                        "Scalar construct failed"
                        f" with args = {(arg, *args)}, kwargs = {kwargs};"
                        f" {e}"
                        )
            else:
                return cls(**kwargs)
        else:
            raise ScalarConstructFailure(
                f"Provided dtype '{dtype}' not an acceptable type"
                " for scalar constructor."
                )

    def __init__(self, **kwargs) -> None:
        self._rectified = False
        super().__init__(**kwargs)

    def rectify(self):
        if not self._rectified:
            mem = self.memory
            try:
                self.memory = self.dtype(mem)
                self._rectified = True
            except TypeError:
                if mem is Ellipsis:
                    self.memory = self._prev
                    self._rectified = True
                if self.isnull:
                    raise NullValueDetected
                elif hasattr(mem, '_funcy_setvariable__'):
                    self.memory._funcy_setvariable__(self)
                    self.rectify()
                else:
                    self.nullify()
                    if not mem is None:
                        raise TypeError(type(mem))

    def set_value(self, val):
        self._prev = self.memory
        self.memory = val
        self._rectified = False

class ScalarReal(Scalar, _generic.Real):
    def __init__(self, *, dtype = float, **kwargs):
        super().__init__(dtype = dtype, **kwargs)

class ScalarIntegral(Scalar, _generic.Integral):
    def __init__(self, *, dtype = int, **kwargs):
        super().__init__(dtype = dtype, **kwargs)

###############################################################################
''''''
###############################################################################