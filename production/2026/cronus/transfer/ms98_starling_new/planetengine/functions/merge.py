from . import _function
from . import _convert
from ._construct import _construct as _master_construct
from . import component

def _construct(*args, **kwargs):
    func = _master_construct(Merge, *args, **kwargs)
    return func

class Merge(_function.Function):

    opTag = 'Merge'

    def __init__(self, *args, **kwargs):

        inVars = _convert.convert(args)

        for inVar in inVars:
            if not inVar.varDim == 1:
                raise Exception

        dTypes = set([inVar.dType for inVar in inVars])
        if not len(dTypes) == 1:
            raise Exception
        dType = list(dTypes)[0]

        substrates = set([inVar.substrate for inVar in inVars])
        if not len(substrates) == 1:
            raise Exception

        substrate = list(substrates)[0]
        if substrate is None:
            raise Exception

        meshbased = all(
            [inVar.meshbased for inVar in inVars]
            )
        dimension = len(inVars)
        if meshbased:
            var = substrate.add_variable(dimension, dType)
        else:
            var = substrate.add_variable(dType, dimension)

        self.stringVariants = {}
        self.inVars = list(inVars)
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

    def _partial_update(self):
        for index, inVar in enumerate(self.inVars):
            self.var.data[:, index] = \
                inVar.data[:, 0]

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def annulise(inVar):
    inVar = _convert.convert(inVar)
    comps = []
    comps.append(component.ang(inVar))
    comps.append(component.rad(inVar))
    if inVar.mesh.dim == 3:
        comps.append(component.coang(inVar))
    var = _construct(*comps)
    return var

def cartesianise(inVar):
    inVar = _convert.convert(inVar)
    comps = []
    comps.append(component.x(inVar))
    comps.append(component.y(inVar))
    if inVar.mesh.dim == 3:
        comps.append(component.z(inVar))
    var = _construct(*comps)
    return var
