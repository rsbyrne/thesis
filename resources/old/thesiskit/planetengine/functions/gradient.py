from underworld import function as fn

from . import _convert
from . import _function
from ._construct import _construct as _master_construct
from . import component as _component
from . import projection as _projection

def _construct(*args, **kwargs):
    func = _master_construct(Gradient, *args, **kwargs)
    return func

class Gradient(_function.Function):

    opTag = 'Gradient'

    def __init__(self, inVar, *args, **kwargs):

        inVar = _convert.convert(inVar)
        if not inVar.varType == 'meshVar':
            inVar = _projection.default(inVar)
        var = inVar.var.fn_gradient

        self.stringVariants = {}
        self.inVars = [inVar]
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def mag(*args, **kwargs):
    gradVar = _construct(*args, **kwargs)
    return _component.mag(gradVar, **kwargs)

def rad(*args, **kwargs):
    gradVar = _construct(*args, **kwargs)
    return _component.rad(gradVar, **kwargs)

def ang(*args, **kwargs):
    gradVar = _construct(*args, **kwargs)
    return _component.ang(gradVar, **kwargs)

def coang(*args, **kwargs):
    gradVar = _construct(*args, **kwargs)
    return _component.coang(gradVar, **kwargs)

def x(*args, **kwargs):
    gradVar = _construct(*args, **kwargs)
    return _component.x(gradVar, **kwargs)

def y(*args, **kwargs):
    gradVar = _construct(*args, **kwargs)
    return _component.y(gradVar, **kwargs)

def z(*args, **kwargs):
    gradVar = _construct(*args, **kwargs)
    return _component.z(gradVar, **kwargs)
