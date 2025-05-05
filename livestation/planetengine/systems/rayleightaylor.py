import underworld as uw
from underworld import function as fn
import math
import numpy as np

from planetengine.systems import System

class RayleighTaylor(System):

    species = "rayleightaylor"

    def __init__(
        self,
        *args,
        res = 32,
        f = 0.54,
        aspect = 1.,
        visc_ref = 1.,
        visc_ratio = 1.,
        density_ref = 1.,
        density_ratio = 0.,
        **kwargs
        ):

        ### MESH & MESH VARIABLES ###

        maxf = 0.999
        if f == 'max' or f == 1.:
            f = maxf
        else:
            assert f <= maxf

        length = 1.
        outerRad = 1. / (1. - f)
        radii = (outerRad - length, outerRad)

        maxAspect = math.pi * sum(radii) / length
        if aspect == 'max':
            aspect = maxAspect
            periodic = True
        else:
            assert aspect < maxAspect
            periodic = False

        width = length**2 * aspect * 2. / (radii[1]**2 - radii[0]**2)
        midpoint = math.pi / 2.
        angExtentRaw = (midpoint - 0.5 * width, midpoint + 0.5 * width)
        angExtentDeg = [item * 180. / math.pi for item in angExtentRaw]
        angularExtent = [
            max(0., angExtentDeg[0]),
            min(360., angExtentDeg[1] + abs(min(0., angExtentDeg[0])))
            ]
        angLen = angExtentRaw[1] - angExtentRaw[0]

        assert res % 4 == 0
        radRes = res
        angRes = 4 * int(angLen * (int(radRes * radii[1] / length)) / 4)
        elementRes = (radRes, angRes)

        mesh = uw.mesh.FeMesh_Annulus(
            elementRes = elementRes,
            radialLengths = radii,
            angularExtent = angularExtent,
            periodic = [False, periodic]
            )

        velocityField = mesh.add_variable(2)
        pressureField = mesh.subMesh.add_variable(1)

        swarm = uw.swarm.Swarm(mesh, particleEscape = True)
        materialField = swarm.add_variable(
            dataType = "int",
            count = 1
            )
        swarmLayout = uw.swarm.layouts.PerCellSpaceFillerLayout(
            swarm = swarm,
            particlesPerCell = 20
            )
        swarm.populate_using_layout(swarmLayout)
        repopulator = uw.swarm.PopulationControl(
            swarm,
            aggressive = True,
            splitThreshold = 0.15,
            maxDeletions = 2,
            maxSplits = 10,
            particlesPerCell = 10
            )

        ### BOUNDARIES ###

        inner = mesh.specialSets["inner"]
        outer = mesh.specialSets["outer"]
        sides = mesh.specialSets["MaxJ_VertexSet"] + mesh.specialSets["MinJ_VertexSet"]

        if periodic:
            velBC = uw.conditions.RotatedDirichletCondition(
                variable = velocityField,
                indexSetsPerDof = (inner + outer, inner + outer),
                basis_vectors = (mesh.bnd_vec_normal, mesh.bnd_vec_tangent)
                )
        else:
            velBC = uw.conditions.RotatedDirichletCondition(
                variable = velocityField,
                indexSetsPerDof = (inner + outer, sides + inner + outer),
                basis_vectors = (mesh.bnd_vec_normal, mesh.bnd_vec_tangent)
                )

        ### FUNCTIONS ###

        vc = uw.mesh.MeshVariable(mesh = mesh, nodeDofCount = 2)
        vc_eqNum = uw.systems.sle.EqNumber(vc, False )
        vcVec = uw.systems.sle.SolutionVector(vc, vc_eqNum)

        denseIndex = 0
        lightIndex = 1
        densityMap = {lightIndex: density_ratio * density_ref, denseIndex: density_ref}
        densityFn = fn.branching.map(fn_key = materialField, mapping = densityMap)
        buoyancyFn = densityFn * -1. * mesh.unitvec_r_Fn

        ### RHEOLOGY ###

        viscosityMap = {lightIndex: visc_ratio * visc_ref, denseIndex: visc_ref}
        viscosityFn  = fn.branching.map(fn_key = materialField, mapping = viscosityMap)

        ### SYSTEMS ###

        stokes = uw.systems.Stokes(
            velocityField = velocityField,
            pressureField = pressureField,
            conditions = [velBC,],
            fn_viscosity = viscosityFn,
            fn_bodyforce = buoyancyFn,
            _removeBCs = False,
            )

        solver = uw.systems.Solver(stokes)

        advector = uw.systems.SwarmAdvector(
            swarm = swarm,
            velocityField = vc,
            order = 2
            )

        ### SOLVING ###

        def postSolve():
            # realign solution using the rotation matrix on stokes
            uw.libUnderworld.Underworld.AXequalsY(
                stokes._rot._cself,
                stokes._velocitySol._cself,
                vcVec._cself,
                False
                )
            # remove null space - the solid body rotation velocity contribution
            uw.libUnderworld.StgFEM.SolutionVector_RemoveVectorSpace(
                stokes._velocitySol._cself,
                stokes._vnsVec._cself
                )

        def solve():
            velocityField.data[:] = 0.
            solver.solve(
                nonLinearIterate = False,
                callback_post_solve = postSolve,
                )
            uw.libUnderworld.Underworld.AXequalsX(
                stokes._rot._cself,
                stokes._velocitySol._cself,
                False
                )

        def update():
            solve()

        def integrate():
            dt = advector.get_max_dt()
            advector.integrate(dt)
            repopulator.repopulate()
            return dt

        stress = velocityField * viscosityFn
        stress.varName = 'stress'
        materialField.varName = 'material'
        velocityField.varName = 'velocity'

        super().__init__(
            varsOfState = {'materialField': materialField},
            obsVars = {'stress': stress, 'material': materialField},
            _update = update,
            _integrate = integrate,
            _locals = locals(),
            args = args,
            kwargs = kwargs
            )

CLASS = RayleighTaylor
