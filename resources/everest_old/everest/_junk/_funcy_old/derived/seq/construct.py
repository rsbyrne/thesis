###############################################################################
''''''
###############################################################################

import numbers as _numbers
from collections.abc import Iterable as _Iterable

from . import _Derived, _generic
from .seq import Seq as _Seq
from .nvar import N as _N
from .algorithmic import Algorithmic as _Algorithmic
from .arbitrary import Arbitrary as _Arbitrary
from .continuous import Continuum as _Continuum
from .discrete import (
    Discrete as _Discrete,
    Regular as _Regular,
    Shuffle as _Shuffle,
    Procedural as _Procedural,
    )
from . import samplers as _samplers

from .exceptions import *

is_real = lambda s: all((
    isinstance(s, _generic.Real),
    not isinstance(s, _generic.Integral),
    ))

def construct_seq(arg = None, /) -> _Seq:
    if isinstance(arg, _Derived):
        if hasattr(arg, '_abstract'):
            return _Algorithmic._construct(arg)
        else:
            raise NotYetImplemented
    elif type(arg) is slice:
        start, stop, step = arg.start, arg.stop, arg.step
        if any(is_real(s) for s in (start, stop, step)):
            return _Continuum._construct(start, stop, step)
        else:
            if isinstance(step, _samplers.Sampler):
                return step._construct(start, stop)
            elif isinstance(step, _generic.String):
                return _Shuffle._construct(start, stop, step)
            else:
                return _Regular._construct(start, stop, step)
    elif isinstance(arg, _Iterable):
        return _Arbitrary._construct(*arg)
    else:
        raise TypeError(
            "Could not understand seq input of type:", type(arg)
            )

###############################################################################
''''''
###############################################################################