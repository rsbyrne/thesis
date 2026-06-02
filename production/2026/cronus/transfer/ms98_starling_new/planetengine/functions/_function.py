import numpy as np

from . import _planetvar
from . import _basetypes
from . import _reduction
from .. import meshutils

class Function(_planetvar.PlanetVar):

    def __init__(self, *args, **kwargs):

        self._check_inVars()
        self._detect_substrates()
        self._detect_attributes()
        # if not self.varType == 'constFn':
        #     self._detect_scales_bounds()
        self._hashVars = self.inVars

        super().__init__(**kwargs)

    def _check_inVars(self):
        for inVar in self.inVars:
            if not isinstance(inVar, _planetvar.PlanetVar):
                raise Exception(
                    "Type " + str(type(inVar)) + " is not _planetvar.PlanetVar."
                    )

    def _detect_substrates(self):
        meshes = set()
        substrates = set()
        for inVar in self.inVars:
            if hasattr(inVar, 'mesh'):
                if not inVar.mesh is None:
                    meshes.add(inVar.mesh)
            if hasattr(inVar, 'substrate'):
                if not inVar.substrate is None:
                    substrates.add(inVar.substrate)
        subMeshes = set()
        for mesh in meshes:
            try: subMeshes.add(mesh.subMesh)
            except AttributeError: pass
        meshes = {m for m in meshes if not m in subMeshes}
        substrates = {s for s in substrates if not s in subMeshes}
        if len(meshes) == 1:
            self.mesh = list(meshes)[0]
            self.meshUtils = meshutils.get_meshUtils(self.mesh)
        elif len(meshes) == 0:
            self.mesh = None
        else:
            raise Exception
        if len(substrates) == 1:
            self.substrate = list(substrates)[0]
        elif len(substrates) == 0:
            self.substrate = None
        else:
            raise Exception

    def _detect_attributes(self):
        if not self.mesh is None and self.substrate is self.mesh:
            self.meshbased = True
            self.varType = 'meshFn'
            sample_data = self.var.evaluate(self.mesh.data[0:1])
        else:
            self.meshbased = False
            if self.substrate is None:
                self.varType = 'constFn'
                sample_data = self.var.evaluate()
            else:
                self.varType = 'swarmFn'
                sample_data = self.var.evaluate(self.substrate.data[0:1])
        self.dType = _planetvar.get_dType(sample_data)
        self.varDim = sample_data.shape[1]
        self._check_vector()

    def _check_vector(self):
        if hasattr(self, 'vector'):
            vector = self.vector
        else:
            vector = None
        if vector is None:
            if not self.mesh is None:
                vector = self.varDim == self.mesh.dim
            else:
                vector = False
        elif vector:
            if not self.varDim == self.mesh.dim:
                raise Exception
        self.vector = vector

    def _output_processing(self, evalOutput):
        if all([
                isinstance(inVar, _reduction.Reduction) \
                    for inVar in self.inVars
                ]):
            val = evalOutput
            for layer in evalOutput.shape:
                val = val[0]
            return np.array(val)
        else:
            return evalOutput

    # def _detect_scales_bounds(self):
    #     fields = []
    #     for inVar in self.inVars:
    #         if type(inVar) == _basetypes.Variable:
    #             fields.append(inVar)
    #         elif isinstance(inVar, Function):
    #             fields.append(inVar)
    #     inscales = []
    #     inbounds = []
    #     for inVar in fields:
    #         if hasattr(inVar, 'scales'):
    #             if inVar.varDim == self.varDim:
    #                 inscales.append(inVar.scales)
    #             else:
    #                 inscales.append(inVar.scales * self.varDim)
    #         else:
    #             inscales.append(
    #                 [['.', '.']] * self.varDim
    #                 ) # i.e. perfectly free
    #         if hasattr(inVar, 'bounds'):
    #             if inVar.varDim == self.varDim:
    #                 inbounds.append(inVar.bounds)
    #             else:
    #                 inbounds.append(inVar.bounds * self.varDim)
    #         else:
    #             inbounds.append(
    #                 [['.'] * self.mesh.dim ** 2] * self.varDim
    #                 ) # i.e. perfectly free
    #     scales = []
    #     for varDim in range(self.varDim):
    #         fixed = not any([
    #             inscale[varDim] == ['.', '.'] \
    #                 for inscale in inscales
    #             ])
    #         if fixed:
    #             scales.append('!')
    #         else:
    #             scales.append('.')
    #     bounds = []
    #     for varDim in range(self.varDim):
    #         dimBounds = []
    #         for index in range(self.mesh.dim ** 2):
    #             fixed = not any([
    #                 inbound[varDim][index] == '.' \
    #                     for inbound in inbounds
    #                 ])
    #             if fixed:
    #                 dimBounds.append('!')
    #             else:
    #                 dimBounds.append('.')
    #         bounds.append(dimBounds)
    #     if not hasattr(self, 'scales'):
    #         self.scales = scales
    #     if not hasattr(self, 'bounds'):
    #         self.bounds = bounds
