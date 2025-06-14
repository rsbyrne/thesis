import underworld as uw
from underworld import function as fn

from . import _function
from . import _convert
from ._construct import _construct as _master_construct
from . import normalise
from . import merge
from . import split
from .. import meshutils

def _construct(*args, **kwargs):
    func = _master_construct(Box, *args, **kwargs)
    return func

class Box(_function.Function):

    opTag = 'Box'

    def __init__(self, unitVar, *args, **kwargs):

        unitVar = _convert.convert(unitVar)
        inMesh = unitVar.mesh

        coordFns = []
        if type(inMesh) == uw.mesh.FeMesh_Annulus:
            ang = normalise.unit(unitVar.var * (1. - inMesh.thetaFn))
            rad = normalise.unit(unitVar.var * inMesh.radiusFn)
            coordFns = [ang, rad]
        else:
            raise Exception("That mesh type is not supported yet.")

        var = merge.default(*coordFns)

        self.stringVariants = {}
        self.inVars = [unitVar,]
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

def default(inMesh, *args, **kwargs):
    if not isinstance(inMesh, uw.mesh._mesh.FeMesh):
        raise Exception("Input must be mesh type.")
    meshUtils = meshutils.get_meshUtils(inMesh)
    unitVar = meshUtils.get_unitVar()
    return _construct(unitVar, *args, **kwargs)

def getall(*args, **kwargs):
    return split.getall(default(*args, **kwargs))
