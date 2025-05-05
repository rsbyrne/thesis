from underworld import function as fn

from . import _convert
from . import _function
from ._construct import _construct as _master_construct
from . import component as _component
from . import projection as _projection

def _construct(*args, **kwargs):
    func = _master_construct(Tensor, *args, **kwargs)
    return func

class Tensor(_function.Function):

    opTag = 'Tensor'

    def __init__(self, inVar, *args, part = 'symmetric', **kwargs):

        inVar = _convert.convert(inVar)

        tensor = getattr(fn.tensor, part)
        var = tensor(inVar)

        self.stringVariants = {part: part}
        self.inVars = [inVar]
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def symmetric(*args, **kwargs):
    return _construct(*args, part = 'symmetric', **kwargs)

def antisymmetric(*args, **kwargs):
    return _construct(*args, part = 'antisymmetric', **kwargs)

def second_invariant(*args, **kwargs):
    return _construct(*args, part = 'second_invariant', **kwargs)

def deviatoric(*args, **kwargs):
    return _construct(*args, part = 'deviatoric', **kwargs)
