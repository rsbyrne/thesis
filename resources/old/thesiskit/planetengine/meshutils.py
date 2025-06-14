from .utilities import get_scales
# from .utilities import get_mesh
from .utilities import hash_var

import underworld as uw
from underworld import function as fn

import numpy as np
import weakref
import random

from everest import mpi

def get_meshUtils(mesh):
    if not hasattr(mesh, 'meshUtils'):
        # POTENTIAL CIRCULAR REFERENCE
        mesh.meshUtils = MeshUtils(mesh)
    return mesh.meshUtils

def makeLocalAnnulus(mesh):
    for proc in range(mpi.size):
        if mpi.rank == proc:
            localAnn = uw.mesh.FeMesh_Annulus(
                elementType = mesh.elementType,
                elementRes = mesh.elementRes,
                radialLengths = mesh.radialLengths,
                angularExtent = mesh.angularExtent,
                periodic = mesh.periodic,
                partitioned = False,
                )
    # mpi.barrier()
    return localAnn

def makeLocalCart(mesh):
    for proc in range(mpi.size):
        if mpi.rank == proc:
            localMesh = uw.mesh.FeMesh_Cartesian(
                elementType = mesh.elementType,
                elementRes = mesh.elementRes,
                minCoord = mesh.minCoord,
                maxCoord = mesh.maxCoord,
                periodic = mesh.periodic,
                partitioned = False,
                )
    # mpi.barrier()
    return localMesh

class MeshUtils:

    def __init__(
            self,
            mesh,
            ):

        if type(mesh) == uw.mesh.FeMesh_Cartesian:
            meshtype = 'normal'

            self.flip = [False, False]

            self.surfaces = {
                'inner': mesh.specialSets['Bottom_VertexSet'],
                'outer': mesh.specialSets['Top_VertexSet'],
                'left': mesh.specialSets['Left_VertexSet'],
                'right': mesh.specialSets['Right_VertexSet'],
                'all': mesh.specialSets['AllWalls_VertexSet']
                }
            if mesh.dim == 2:
                self.comps = {
                    'x':fn.misc.constant((1., 0.)),
                    'y':fn.misc.constant((0., 1.)),
                    'ang':fn.misc.constant((1., 0.)),
                    'rad':fn.misc.constant((0., -1.)),
                    }
            elif mesh.dim == 3:
                self.comps = {
                    'x':fn.misc.constant((1., 0., 0.)),
                    'y':fn.misc.constant((0., 1., 0.)),
                    'z':fn.misc.constant((0., 0., 1.)),
                    'ang':fn.misc.constant((1., 0., 0.)),
                    'coang':fn.misc.constant((0., 1., 0.)),
                    'rad':fn.misc.constant((0., 0., -1.)),
                    }
                self.surfaces['front'] = mesh.specialSets['MinK_VertexSet']
                self.surfaces['back'] = mesh.specialSets['MaxK_VertexSet']

        elif type(mesh) == uw.mesh.FeMesh_Annulus:
            meshtype = 'normal'

            # self.flip = [True, False] # left to right, bottom to top
            # _flip_cfs = [int(not boolean) * 2. - 1. for boolean in self.flip]
            #
            # self.comps = {
            #     'x':fn.misc.constant((1., 0.)),
            #     'y':fn.misc.constant((0., 1.)),
            #     'ang': _flip_cfs[0] * mesh.unitvec_theta_Fn,
            #     'rad': _flip_cfs[1] * mesh.unitvec_r_Fn,
            #     }
            self.comps = {
                'x':fn.misc.constant((1., 0.)),
                'y':fn.misc.constant((0., 1.)),
                'ang': -mesh.unitvec_theta_Fn,
                'rad':  mesh.unitvec_r_Fn,
                }
            self.surfaces = {
                'inner': mesh.specialSets['inner'],
                'outer': mesh.specialSets['outer'],
                'left': mesh.specialSets['MaxJ_VertexSet'],
                'right': mesh.specialSets['MinJ_VertexSet'],
                'all': mesh.specialSets['AllWalls_VertexSet']
                }
            self.surfaces['ang'] = \
                self.surfaces['left'] \
                + self.surfaces['right']
            self.surfaces['rad'] = \
                self.surfaces['inner'] \
                + self.surfaces['outer']
        else:
            meshtype = 'abnormal'
            self.comps = {}
            self.surfaces = {}

        if meshtype == 'normal':
            self.wallsList = [
                self.surfaces['outer'],
                self.surfaces['inner'],
                self.surfaces['left'],
                self.surfaces['right']
                ]
            try:
                wallsList.append(self.surfaces['front'])
                wallsList.append(self.surfaces['back'])
            except:
                pass

            self.__dict__.update(self.comps)
            self.__dict__.update(self.surfaces)

            self.scales = get_scales(mesh.data)

            volInt = uw.utils.Integral(
                1.,
                mesh,
                )
            outerInt = uw.utils.Integral(
                1.,
                mesh,
                integrationType = 'surface',
                surfaceIndexSet = self.outer
                )
            innerInt = uw.utils.Integral(
                1.,
                mesh,
                integrationType = 'surface',
                surfaceIndexSet = self.inner
                )

            deformable = False # CHANGE WHEN DEFORMABLE MESHES SUPPORTED
            if not deformable:

                volIntVal = volInt.evaluate()[0]
                outerIntVal = outerInt.evaluate()[0]
                innerIntVal = innerInt.evaluate()[0]

                self.integral = lambda: volIntVal
                self.integral_outer = lambda: outerIntVal
                self.integral_inner = lambda: innerIntVal

            else:

                self.integral = lambda: volInt.evaluate()[0]
                self.integral_outer = lambda: outerInt.evaluate()[0]
                self.integral_inner = lambda: innerInt.evaluate()[0]

            self.integrals = {
                'inner': self.integral_inner,
                'outer': self.integral_outer,
                'volume': self.integral,
                }

            xs = np.linspace(mesh.data[:,0].min(), mesh.data[:,0].max(), 100)
            ys = np.linspace(mesh.data[:,1].min(), mesh.data[:,1].max(), 100)
            self.cartesianScope = np.array(
                np.meshgrid(xs, ys)).T.reshape([-1, 2]
                )

        self.mesh = weakref.ref(mesh)

    def get_full_local_mesh(self):
        if not hasattr(self, 'fullLocalMesh'):
            self.fullLocalMesh = makeLocalAnnulus(self.mesh())
        return self.fullLocalMesh

    def get_unitVar(self):
        if not hasattr(self, 'unitVar'):
            self.unitVar = self.mesh().add_variable(1)
            self.unitVar.data[:] = 1.
        return self.unitVar

    meshifieds = {}

    def meshify(
            self,
            inVar,
            vector = False,
            update = True,
            rounding = 6
            ):
        if type(inVar) == uw.mesh._meshvariable.MeshVariable:
            outVar = inVar
        else:
            random.seed(inVar.__hash__() + rounding)
            in_hash = random.randint(1e18, 1e19 - 1)
            random.seed()
            try:
                outVar = self.meshifieds[in_hash]()
                assert not outVar is None
            except:
                if vector:
                    outVar = self._make_vectorVar()
                else:
                    outVar = self._make_scalarVar()
                self.meshifieds[in_hash] = weakref.ref(outVar)
                outVar.lasthash = 0
                outVar.project = lambda: self.project(
                    outVar,
                    inVar,
                    rounding,
                    _lasthash = outVar.lasthash,
                    _update_lasthash = True
                    )
            if update:
                outVar.project()
        return outVar

    def project(
            self,
            meshVar,
            inFn,
            rounding = 6,
            _lasthash = 0,
            _update_lasthash = False
            ):
        currenthash = hash_var(inFn)
        if not currenthash == _lasthash:
            if meshVar.nodeDofCount == meshVar.mesh.dim:
                projector = self.get_vectorProjector()
            else:
                projector = self.get_scalarProjector()
            projector.fn = inFn
            projector.solve()
            meshVar.data[:] = projector._meshVariable.data
            allwalls = self.surfaces['all']
            meshVar.data[allwalls.data] = \
                inFn.evaluate(allwalls)
            meshVar.data[:] = np.round(
                meshVar.data,
                rounding
                )
            if _update_lasthash:
                meshVar.lasthash = currenthash

    def get_scalarProjector(self):
        if not hasattr(self, 'scalarProjector'):
            self._make_scalarProjector()
        return self.scalarProjector

    def get_vectorProjector(self):
        if not hasattr(self, 'vectorProjector'):
            self._make_vectorProjector()
        return self.vectorProjector

    def _make_scalarProjector(self):
        toVar = self._make_scalarVar()
        projector = uw.utils.MeshVariable_Projection(
            toVar,
            toVar
            )
        self.scalarProjector = projector

    def _make_vectorProjector(self):
        toVar = self._make_vectorVar()
        projector = uw.utils.MeshVariable_Projection(
            toVar,
            toVar
            )
        self.vectorProjector = projector

    def _make_scalarVar(self):
        outVar = self.mesh().add_variable(1)
        outVar.data[:] = 0.
        return outVar

    def _make_vectorVar(self):
        outVar = self.mesh().add_variable(self.mesh().dim)
        outVar.data[:] = 0.
        return outVar

    # def _get_scalar_dummyVar(self):
    #     if not hasattr(self, 'scalarDummyVar'):
    #         self.scalarDummyVar = self._make_scalarVar()
    #     else:
    #         self.scalarDummyVar = self._get_scalar_dummyVar()
    #     return self.scalarDummyVar
    #
    # def _get_vector_dummyVar(self):
    #     if not hasattr(self, 'vectorDummyVar'):
    #         self.vectorDummyVar = self._make_scalarVar()
    #     else:
    #         self.scalarDummyVar = self._get_scalar_dummyVar()
    #     return self.scalarDummyVar
    #
