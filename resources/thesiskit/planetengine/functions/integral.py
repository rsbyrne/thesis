import underworld as uw

from . import _convert
from . import _reduction
from . import _basetypes
from ._construct import _construct as _master_construct
from . import surface as _surface
from . import handlenan as _handlenan

def _construct(*args, **kwargs):
    func = _master_construct(Integral, *args, **kwargs)
    return func

class Integral(_reduction.Reduction):

    opTag = 'Integral'

    def __init__(self, inVar, *args, surface = 'volume', **kwargs):

        inVar = _convert.convert(inVar)

        if type(inVar) == _surface.Surface:
            raise Exception(
                "Surface type not accepted; try Integral.auto method."
                )
        elif isinstance(inVar, _reduction.Reduction):
            raise Exception

        intMesh = inVar.meshUtils.integrals[surface]
        if surface == 'volume':
            intField = uw.utils.Integral(
                inVar,
                inVar.mesh
                )
        else:
            indexSet = inVar.meshUtils.surfaces[surface]
            intField = uw.utils.Integral(
                inVar,
                inVar.mesh,
                integrationType = 'surface',
                surfaceIndexSet = indexSet
                )

        def int_eval():
            val = intField.evaluate()[0]
            val /= intMesh()
            return val
        var = _basetypes.Parameter(int_eval)

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

def auto(*args, **kwargs):
    inVar = _convert.convert(args[0])
    if type(inVar) == _surface.Surface:
        surface = inVar.stringVariants['surface']
        inVar = inVar.inVar
    else:
        surface = 'volume'
    return _construct(inVar, *args, surface = surface, **kwargs)
