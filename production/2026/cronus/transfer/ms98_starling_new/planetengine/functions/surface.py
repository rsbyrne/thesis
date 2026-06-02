import numpy as np

import underworld as uw
fn = uw.function

from . import _convert
from . import _reduction
from . import _basetypes
from ._construct import _construct as _master_construct
from ..utilities import globalise_array

def _construct(*args, **kwargs):
    func = _master_construct(Surface, *args, **kwargs)
    return func

class Surface(_reduction.Reduction):

    opTag = 'Surface'

    def __init__(self, inVar, *args, surface = 'inner', **kwargs):

        inVar = _convert.convert(inVar)

        if not hasattr(inVar, 'mesh'):
            raise Exception

        self._surface = \
            inVar.mesh.meshUtils.surfaces[surface]

        def evalFn():
            val = inVar.evaluate(self._surface)
            val = globalise_array(val, self._surface)
            return val.flatten()
        var = _basetypes.Parameter(evalFn)

        self.stringVariants = {'surface': surface}
        self.inVars = [inVar]
        self.parameters = [var]
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def volume(*args, **kwargs):
    return _construct(*args, surface = 'volume', **kwargs)

def inner(*args, **kwargs):
    return _construct(*args, surface = 'inner', **kwargs)

def outer(*args, **kwargs):
    return _construct(*args, surface = 'outer', **kwargs)

def left(*args, **kwargs):
    return _construct(*args, surface = 'left', **kwargs)

def right(*args, **kwargs):
    return _construct(*args, surface = 'right', **kwargs)

def front(*args, **kwargs):
    return _construct(*args, surface = 'front', **kwargs)

def back(*args, **kwargs):
    return _construct(*args, surface = 'back', **kwargs)
