###############################################################################
'''The module defining the 'Operation' Derived type.'''
###############################################################################

import builtins as _builtins
import operator as _operator
import math as _math

from . import _abstract, _Funcy, _special

from .derived import Derived as _Derived
from .group import Group as _Group
from .map import Map as _Map

def get_opfn(name: str):
    opfn = None
    for source in (_builtins, _operator, _math):
        try:
            opfn = getattr(source, name)
            break
        except AttributeError:
            pass
    if opfn is None:
        raise AttributeError(name)
    return opfn

class Operation(_Derived):
    def __init__(self, callargs, callkwargs, /, *, opkey):
        if not isinstance(callargs, _Funcy):
            if callargs:
                callargs = _Group(*callargs)
            else:
                callargs = _special.emptyseq
        if not isinstance(callkwargs, _Funcy):
            if callkwargs:
                callkwargs = _Map(*zip(*dict(callkwargs).items()))
            else:
                callkwargs = _special.emptymap
        super().__init__(callargs, callkwargs, opkey = opkey)
        opfn = get_opfn(opkey)
        self.evaluate = lambda args, kwargs: opfn(*args, **kwargs)

def operation(name: str):
    '''Partial constructor for Operation.'''
    def construct(*args, **kwargs):
        return Operation(list(args), list(kwargs), opkey = name)
    return construct

###############################################################################
###############################################################################
