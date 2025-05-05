import numpy as np

from underworld import function as fn

from . import _convert
from . import _function
from . import _basetypes
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Clip, *args, **kwargs)
    return func

class Clip(_function.Function):

    opTag = 'Clip'

    def __init__(
            self,
            inVar,
            lBnd = None,
            lClipVal = 'null',
            uBnd = None,
            uClipVal = 'null',
            **kwargs
            ):

        inVar = _convert.convert(inVar)
        inVars = [inVar]
        stringVariants = {}
        parameters = []
        clauses = []
        nullVal = [np.nan for dim in range(inVar.varDim)]

        if lBnd is None:
            stringVariants['lower'] = 'open'
        else:
            lBnd = _convert.convert(lBnd)
            if not lBnd in inVars:
                inVars.append(lBnd)
            lBnd = _basetypes.Parameter(lBnd._minFn)
            parameters.append(lBnd)
            if lClipVal is 'null':
                lClipVal = nullVal
                stringVariants['lower'] = 'null'
            elif lClipVal == 'fill':
                lClipVal = lBnd
                stringVariants['lower'] = 'fill'
            else:
                raise Exception
            clauses.append((inVar < lBnd, lClipVal))

        if uBnd is None:
            stringVariants['lower'] = 'open'
        else:
            uBnd = _convert.convert(uBnd)
            if not uBnd in inVars:
                inVars.append(uBnd)
            uBnd = _basetypes.Parameter(uBnd._maxFn)
            parameters.append(uBnd)
            if uClipVal is 'null':
                uClipVal = nullVal
                stringVariants['upper'] = 'null'
            elif uClipVal == 'fill':
                uClipVal = uBnd
                stringVariants['upper'] = 'fill'
            else:
                raise Exception
            clauses.append((inVar > uBnd, uClipVal))

        clauses.append((True, inVar))

        if stringVariants['lower'] == stringVariants['upper']:
            stringVariants['both'] = stringVariants['lower']
            del stringVariants['lower']
            del stringVariants['upper']

        var = fn.branching.conditional(clauses)

        self.stringVariants = stringVariants
        self.inVars = list(inVars)
        self.parameters = parameters
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def torange(inVar, clipVar, **kwargs):
    inVar, clipVar = _convert.convert(inVar, clipVar)
    return _construct(
        inVar,
        lBnd = clipVar,
        uBnd = clipVar,
        **kwargs
        )
