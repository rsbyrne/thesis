from . import _function
from . import _convert
from . import _basetypes
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Normalise, *args, **kwargs)
    return func

class Normalise(_function.Function):

    opTag = 'Normalise'

    def __init__(self, baseVar, normVar, *args, **kwargs):

        baseVar, normVar = inVars = _convert.convert(baseVar, normVar)

        inMins = _basetypes.Parameter(baseVar._minFn)
        inRanges = _basetypes.Parameter(baseVar._rangeFn)
        normMins = _basetypes.Parameter(normVar._minFn)
        normRanges = _basetypes.Parameter(normVar._rangeFn)

        var = (baseVar - inMins) / inRanges * normRanges + normMins

        self.stringVariants = {}
        self.inVars = list(inVars)
        self.parameters = [inMins, inRanges, normMins, normRanges]
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def unit(baseVar, *args, **kwargs):
    return _construct(baseVar, [0., 1.], **kwargs)
