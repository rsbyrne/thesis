###############################################################################
''''''
###############################################################################


import itertools as _itertools

from . import _utilities

from .pleroma import Pleroma as _Pleroma
from .primitive import Primitive as _Primitive

from . import exceptions as _exceptions


class BadParameter(_exceptions.ParameterisationException):
    '''Raised when an unrecognised parameter type is detected.'''

    __slots__ = ('param',)

    def __init__(self, param, /):
        self.param = param

    def message(self, /):
        yield from super().message()
        yield "when an object of unrecognised type was passed as a parameter."
        try:
            rep = repr(self.param)
        except Exception as exc:
            yield 'While writing this message, another exception occurred:'
            yield str(exc)
        else:
            yield 'The object looked something like this:'
            yield rep


class PtolemaicBase(metaclass=_Pleroma):
    '''
    The base class of all object types
    understood as inputs for the Ptolemaic system.
    '''


_ = PtolemaicBase.register(_Primitive)


class Ptolemaic(PtolemaicBase):

    BadParameter = BadParameter

    @classmethod
    def check_param(cls, arg, /):
        if not isinstance(arg, PtolemaicBase):
            try:
                meth = cls.checktypes[type(arg)]
            except KeyError as exc:
                raise BadParameter(arg) from exc
            else:
                arg = meth(arg)
        return arg

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return type(cls).parameterise(cls,
            *map(cls.check_param, args),
            **dict(zip(kwargs, map(cls.check_param, kwargs.values()))),
            )

    @classmethod
    def instantiate(cls, params, /):
        return type(cls).instantiate(cls, params)

    @classmethod
    def construct(cls, /, *args, **kwargs):
        return type(cls).construct(cls, *args, **kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return type(cls).__class_getitem__(cls, arg)

    @classmethod
    def yield_checktypes(cls, /):
        return
        yield

    @classmethod
    def _cls_extra_init_(cls, /):
        cls.checktypes = _utilities.TypeMap(cls.yield_checktypes())

    def __init__(self, /):
        pass

    def _repr(self, /):
        return self.params.__str__()

    @classmethod
    def _cls_repr(cls, /):
        if cls._concrete:
            cls = cls.basecls
        return cls.__qualname__

    @_utilities.caching.soft_cache(None)
    def __repr__(self, /):
        return f"{self._cls_repr()}({self._repr()})"


###############################################################################
###############################################################################
