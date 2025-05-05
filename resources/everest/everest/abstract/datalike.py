###############################################################################
''''''
###############################################################################

import numbers as _numbers
from functools import cached_property as _cached_property

import numpy as _np

from .abstract import EverestABC as _EverestABC

class Datalike(_EverestABC):
    _defaultdtype = object
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Datalike:
            if any("_defaultdtype" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
    @classmethod
    def _check_dtype(cls, dtype) -> type:
        if type(dtype) is str:
            import numpy as np
            dtype = eval(dtype)
        if isinstance(dtype, _np.dtype):
            dtype = _np.dtype.type
        if not type(dtype) is type:
            raise TypeError(
                "Provided dtype"
                " must be either a data type or a str evaluable as such."
                )
        if not issubclass(dtype, (default := cls._defaultdtype)):
            raise TypeError(
                f"Provided dtype {dtype} is not a subclass of {default}"
                )
        return dtype
    @_cached_property
    def dtype(self) -> type:
        try:
            return self._check_dtype(self._dtype)
        except AttributeError:
            return self._defaultdtype

class String(Datalike):
    _defaultdtype = str
_ = String.register(String._defaultdtype)

class Bool(Datalike):
    _defaultdtype = bool
_ = Bool.register(Bool._defaultdtype)
_ = Bool.register(_np.bool_)

class Numerical(Datalike):
    _defaultdtype = _numbers.Number

class Number(Numerical):
    ...
_ = Number.register(Number._defaultdtype)

class Complex(Number):
    _defaultdtype = _numbers.Complex
_ = Complex.register(Complex._defaultdtype)

class Real(Complex):
    _defaultdtype = _numbers.Real
_ = Real.register(Real._defaultdtype)

class Rational(Real):
    _defaultdtype = _numbers.Rational
_ = Rational.register(Rational._defaultdtype)

class Integral(Rational):
    _defaultdtype = _numbers.Integral
_ = Integral.register(Integral._defaultdtype)

class Array(Numerical):
    ...
_ = Array.register(_np.ndarray)

###############################################################################
###############################################################################
