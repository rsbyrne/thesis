###############################################################################
''''''
###############################################################################

from collections.abc import Sequence as _Sequence
from typing import Optional as _Optional, Union as _Union

import numpy as _np

from . import _generic
from .numerical import (
    Numerical as _Numerical,
    NumericalConstructFailure,
    )

from .exceptions import *

class ArrayConstructFailure(NumericalConstructFailure):
    ...

class Array(_Numerical, _generic.Array):

    __slots__ = (
        '_shape',
        '_memory',
        )

    @classmethod
    def _construct(cls,
            arg: _Optional[_Union[type, _Sequence, _np.ndarray]] = None,
            /,
            shape: _Optional[tuple] = None,
            *args,
            **kwargs,
            ) -> _Numerical:
        if len(args):
            raise ArrayConstructFailure(
                "Cannot pass multiple args to array constructor"
                )
        kwargs = kwargs.copy()
        skipcheck = False
        if not arg is None:
            try:
                dtype = cls._check_dtype(arg)
                if 'dtype' in kwargs:
                    raise ArrayConstructFailure(
                        f"Cannot provide dtype as both arg and kwarg."
                        )
                kwargs['dtype'] = dtype
                if shape is None:
                    raise ArrayConstructFailure(
                        "No shape arg provided or otherwise deductible."
                        )
                else:
                    kwargs['shape'] = shape
                skipcheck = True
            except TypeError: # deduce params from array-like positional arg
                if not isinstance(arg, _np.ndarray):
                    try:
                        arg = _np.array(arg)
                    except Exception as e:
                        raise ArrayConstructFailure(
                            f"Exception when converting arg"
                            " to numpy array type: {e}"
                            )
                if 'shape' in kwargs:
                    if not arg2 is None:
                        raise ArrayConstructFailure(
                            f"Multiple args/kwargs interpretable as shape."
                            )
                else:
                    kwargs['shape'] = arg.shape
                if shape is None:
                    kwargs['shape'] = arg.shape
                else:
                    kwargs['shape'] = shape
                if not 'dtype' in kwargs: kwargs['dtype'] = arg.dtype.type
                if not 'initVal' in kwargs: kwargs['initVal'] = arg
        try:
            dtype = kwargs['dtype']
        except KeyError:
            raise ArrayConstructFailure(
                "No 'dtype' kwarg or arg interpretable as a datatype"
                " was provided to array constructor."
                )
        if not skipcheck:
            try:
                dtype = cls._check_dtype(dtype)
            except TypeError as e:
                raise ArrayConstructFailure(e)
        if not len(kwargs['shape']):
            raise ArrayConstructFailure("Arrays cannot be scalar.")
        try:
            return cls(**kwargs)
        except Exception as e:
            raise ArrayConstructFailure(
                "Array construct failed"
                f" with args = {(arg, *args)}, kwargs = {kwargs};"
                f" {e}"
                )

    def __init__(self, *, dtype, shape, initVal = _np.nan, **kwargs) -> None:
        initVal = _np.full(shape, initVal, dtype = dtype)
        super().__init__(
            dtype = dtype, shape = shape, initVal = initVal,
            **kwargs
            )
        self._shape = shape
        self._memory = self.memory

    @property
    def shape(self):
        return self._shape

    def rectify(self):
        ...
    def set_value(self, val):
        try:
            self.memory[...] = val
        except NullValueDetected: # because self.memory is null
            self.memory = self._memory # reset to array-like memory
            self.memory[...] = val
        except ValueError as e:
            raise e(val)

    def __setitem__(self, index, val):
        try:
            self.memory[index] = val
        except NullValueDetected:
            self.memory = self._memory
            self.memory[index] = val
        except ValueError as e:
            print(val)
            raise e
        self.refresh()
    def __len__(self):
        return self.shape[0]

construct_array = Array._construct

###############################################################################
''''''
###############################################################################