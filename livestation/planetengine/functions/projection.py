import numpy as np

import underworld as uw

from . import _function
from . import _convert
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Projection, *args, **kwargs)
    return func

class Projection(_function.Function):

    opTag = 'Projection'

    def __init__(self, inVar, *args, **kwargs):

        inVar = _convert.convert(inVar)

        var = uw.mesh.MeshVariable(
            inVar.mesh,
            inVar.varDim,
            )
        self._projector = uw.utils.MeshVariable_Projection(
            var,
            inVar,
            )

        self.stringVariants = {}
        self.inVars = [inVar]
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

        self.varType = 'meshVar'

    def _partial_update(self):
        self._projector.solve()
        allwalls = self.meshUtils.surfaces['all']
        self.var.data[allwalls.data] = \
            self.inVar.evaluate(allwalls)
        if self.inVar.dType in ('int', 'boolean'):
            rounding = 1
        else:
            rounding = 6
        self.var.data[:] = np.round(
            self.var.data,
            rounding
            )

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def get_meshVar(inVar, **kwargs):
    inVar = _convert.convert(inVar)
    if not inVar.varType == 'meshVar':
        inVar = _construct(inVar, **kwargs)
    return inVar
