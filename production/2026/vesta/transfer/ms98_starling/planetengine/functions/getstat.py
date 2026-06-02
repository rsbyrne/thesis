from underworld import function as fn

from . import _convert
from . import _reduction
from . import _basetypes
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(GetStat, *args, **kwargs)
    return func

class GetStat(_reduction.Reduction):

    opTag = 'GetStat'

    def __init__(self, inVar, *args, stat = 'mins', **kwargs):

        if not stat in {'mins', 'maxs', 'ranges'}:
            raise Exception

        inVar = _convert.convert(inVar)

        if stat == 'mins':
            var = _basetypes.Parameter(inVar._minFn)
        elif stat == 'maxs':
            var = _basetypes.Parameter(inVar._maxFn)
        elif stat == 'ranges':
            var = _basetypes.Parameter(inVar._rangeFn)
        elif stat == 'scales':
            var = _basetypes.Parameter(inVar._scaleFn)
        else:
            raise ValueError

        self.stringVariants = {'stat': stat}
        self.inVars = [inVar]
        self.parameters = [var]
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def min(*args, **kwargs):
    return _construct(*args, stat = 'mins', **kwargs)

def max(*args, **kwargs):
    return _construct(*args, stat = 'maxs', **kwargs)

def range(*args, **kwargs):
    return _construct(*args, stat = 'ranges', **kwargs)

def scale(*args, **kwargs):
    return _construct(*args, stat = 'scales', **kwargs)
