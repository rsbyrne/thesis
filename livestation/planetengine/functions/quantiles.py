import numpy as np

from underworld import function as fn

from . import _function
from . import _convert
from . import _basetypes
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Quantiles, *args, **kwargs)
    return func

class Quantiles(_function.Function):

    opTag = 'Quantiles'

    def __init__(self, inVar, *args, ntiles = 5, **kwargs):

        inVar = _convert.convert(inVar)

        # if not inVar.varDim == 1:
        #     raise Exception

        interval = _basetypes.Parameter(
            lambda: inVar._rangeFn() / ntiles
            )
        minVal = _basetypes.Parameter(
            inVar._minFn
            )

        clauses = []
        for ntile in range(1, ntiles):
            clause = (
                inVar <= minVal + interval * float(ntile),
                float(ntile)
                )
            clauses.append(clause)
        clauses.append(
            (True, float(ntiles))
            )
        rawvar = fn.branching.conditional(clauses)
        var = fn.branching.conditional([
            (inVar < np.inf, rawvar),
            (True, np.nan)
            ])

        self.stringVariants = {
            'ntiles': str(ntiles)
            }
        self.inVars = [inVar]
        self.parameters = [interval, minVal]
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def median(*args, **kwargs):
    return _construct(*args, ntiles = 2, **kwargs)

def terciles(*args, **kwargs):
    return _construct(*args, ntiles = 3, **kwargs)

def quartiles(*args, **kwargs):
    return _construct(*args, ntiles = 4, **kwargs)

def quintiles(*args, **kwargs):
    return _construct(*args, ntiles = 5, **kwargs)

def deciles(*args, **kwargs):
    return _construct(*args, ntiles = 10, **kwargs)

def percentiles(*args, **kwargs):
    return _construct(*args, ntiles = 100, **kwargs)
