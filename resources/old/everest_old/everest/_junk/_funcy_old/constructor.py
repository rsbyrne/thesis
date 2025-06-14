###############################################################################
''''''
###############################################################################

from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache
    )

import numbers as _numbers
from collections.abc import Iterable as _Iterable

from .exceptions import *

class _Fn:

    from .function import Function
    from . import base
    from . import derived
    from .derived import seq, opConstructor as op

    from .special import (
        null, nullflt, nullint,
        infint, ninfint, infflt, ninfflt, inf, ninf,
        unk, unkflt, unkint,
        )

    def __call__(self, arg = None, /, *args, **kwargs) -> Function:
        if not (len(args) or len(kwargs)) and isinstance(arg, self.Function):
            return arg
        try:
            if arg is None:
                return self.base.construct_base(arg, *args, **kwargs)
            try:
                return self.derived.construct_derived(arg, *args, **kwargs)
            except ConstructFailure:
                return self.base.construct_base(arg, *args, **kwargs)
        except Exception as e:
            raise ConstructFailure(
                "Construct failed"
                f" with args = {(arg, *args)}, kwargs = {kwargs}; {e}"
                )

    def __getitem__(self, arg, /):
        try:
            return self.seq.construct_seq(arg)
        except Exception as e:
            raise ConstructFailure(
                "Construct failed"
                f" with args = {(arg,)}, kwargs = {dict()}; {e}"
                )

    @_cached_property
    def n(self):
        return self.seq.N()
    @_cached_property
    def unseq(self):
        return self.derived.UnSeq

    def __getattr__(self, name):
        return getattr(self.op, name)

Fn = _Fn()

###############################################################################
''''''
###############################################################################
