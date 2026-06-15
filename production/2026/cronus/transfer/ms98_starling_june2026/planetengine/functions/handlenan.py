import numpy as np

from underworld import function as fn

from . import _convert
from . import _function
from ._construct import _construct as _master_construct
from . import getstat

def _construct(*args, **kwargs):
    func = _master_construct(HandleNaN, *args, **kwargs)
    return func

class HandleNaN(_function.Function):

    opTag = 'HandleNaN'

    def __init__(self, inVar, handleVal, *args, **kwargs):

        inVar, handleVal = inVars = _convert.convert(
            inVar,
            handleVal
            )

        compareVal = [
            np.inf for dim in range(inVar.varDim)
            ]
        var = fn.branching.conditional([
            (inVar < compareVal, inVar),
            (True, handleVal),
            ])

        self.stringVariants = {}
        self.inVars = list(inVars)
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def _NaNFloat(inVar, handleFloat, **kwargs):
    inVar = _convert.convert(inVar)
    handleVal = [
        handleFloat for dim in range(inVar.varDim)
        ]
    return _construct(inVar, handleVal = handleVal, **kwargs)

def zero(inVar, **kwargs):
    return _NaNFloat(inVar, 0., **kwargs)

def unit(inVar, **kwargs):
    return _NaNFloat(inVar, 1., **kwargs)

def min(inVar, **kwargs):
    handleVal = _getstat.GetStat.min(inVar)
    return _NaNFloat(inVar, handleVal, **kwargs)

def max(inVar, **kwargs):
    handleVal = _getstat.GetStat.max(inVar)
    return _NaNFloat(inVar, handleVal, **kwargs)
