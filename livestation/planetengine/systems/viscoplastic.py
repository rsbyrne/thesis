import math

import underworld as uw
fn, cd = uw.function, uw.conditions

from planetengine.systems import System
from planetengine.initials.sinusoidal import Sinusoidal
from planetengine.initials.constant import Constant

class Viscoplastic(System):

    optionsKeys = {
        'res', 'courant', 'innerMethod', 'innerTol', 'outerTol', 'penalty',
        'mgLevels'
        }
    paramsKeys = {
        'alpha', 'aspect', 'etaDelta', 'etaRef', 'f', 'flux', 'H', 'kappa',
        'tauDelta', 'tauRef'
        }
    configsKeys = {
        'temperatureField', 'temperatureDotField'
        }

    def __init__(self,
            # OPTIONS
            res = 64,
            courant = 0.5,
            innerMethod = 'superludist',
            innerTol = None,
            outerTol = None,
            penalty = None,
            mgLevels = None,
            nonLinearTolerance = 1e-2,
            nonLinearMaxIterations = 100,
            # PARAMS
            alpha = 1e7,
            aspect = 1.,
            etaDelta = 3e4,
            etaRef = 1.,
            f = 1.,
            flux = None,
            H = 0.,
            kappa = 1.,
            tauDelta = 1e7,
            tauRef = 4e5,
            # CONFIGS
            temperatureField = Sinusoidal(),
            temperatureDotField = None,
            # META
            **kwargs
            ):

        ### MESH ###

        if f == 1. and aspect == 'max':
            raise ValueError
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

        ### VARIABLES ###

        temperatureField = mesh.add_variable(1)
        temperatureDotField = mesh.add_variable(1)
        conductionField = mesh.add_variable(1)
        pressureField = mesh.subMesh.add_variable(1)
        velocityField = mesh.add_variable(2)
        vc = mesh.add_variable(2)

        ### BOUNDARIES ###

        specSets = mesh.specialSets
        inner, outer = specSets['inner'], specSets['outer']
        left, right = specSets['MaxJ_VertexSet'], specSets['MinJ_VertexSet']

        if mesh.periodic[1]: bounded = (inner + outer, None)
        else: bounded = (inner + outer, left + right)
        bndVecs = (mesh.bnd_vec_normal, mesh.bnd_vec_tangent)
        velBC = cd.RotatedDirichletCondition(velocityField, bounded, bndVecs)
        velBCs = [velBC,]

        if flux is None and H == 0.:
            temperatureField.scales = [[0., 1.]]
            temperatureField.bounds = [[0., 1., '.', '.']]
        else:
            temperatureField.scales = [[0., None]]
            temperatureField.bounds = [[0., '.', '.', '.']]

        if flux is None:
            tempBC = cd.DirichletCondition(temperatureField, (inner + outer,))
            tempBCs = [tempBC,]
        else:
            tempBC = cd.DirichletCondition(temperatureField, (outer,))
            tempFluxBC = cd.NeumannCondition(temperatureField, (inner,), flux)
            tempBCs = [tempBC, tempFluxBC]

        ### FUNCTIONS ###

        buoyancyFn = alpha * temperatureField
        heatingFn = fn.misc.constant(H)
        diffusivityFn = fn.misc.constant(kappa)

        ### RHEOLOGY ###

        surfEta = etaRef + etaDelta
        creepViscFn = etaRef + fn.math.pow(etaDelta, 1. - temperatureField)

        depthFn = mesh.radialLengths[1] - mesh.radiusFn
        tau = tauRef + depthFn * tauDelta
        symmetric = fn.tensor.symmetric(vc.fn_gradient)
        secInvFn = fn.tensor.second_invariant(symmetric)
        plasticViscFn = tau / (2. * secInvFn + 1e-18)

        viscosityFn = fn.misc.min(creepViscFn, plasticViscFn)
        viscosityFn = fn.misc.min(surfEta, fn.misc.max(viscosityFn, etaRef))
        viscosityFn = viscosityFn + 0. * velocityField[0]

        ### SYSTEMS ###

        stokes = uw.systems.Stokes(
            velocityField = velocityField,
            pressureField = pressureField,
            conditions = velBCs,
            fn_viscosity = viscosityFn,
            fn_bodyforce = buoyancyFn * mesh.unitvec_r_Fn,
            _removeBCs = False,
            )
        solver = uw.systems.Solver(stokes)
        solver.set_inner_method(innerMethod)
        if not innerTol is None: solver.set_inner_rtol(innerTol)
        if not outerTol is None: solver.set_outer_rtol(outerTol)
        if not penalty is None: solver.set_penalty(penalty)
        if not mgLevels is None: solver.set_mg_levels(mgLevels)

        advDiff = uw.systems.AdvectionDiffusion(
            phiField = temperatureField,
            phiDotField = temperatureDotField,
            velocityField = vc,
            fn_diffusivity = diffusivityFn,
            fn_sourceTerm = heatingFn,
            conditions = tempBCs
            )

        ### SOLVING ###

        vc_eqNum = uw.systems.sle.EqNumber(vc, False)
        vcVec = uw.systems.sle.SolutionVector(vc, vc_eqNum)

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

        def update():
            velocityField.data[:] = 0.
            solver.solve(
                nonLinearIterate = True,
                nonLinearTolerance = nonLinearTolerance,
                nonLinearMaxIterations = nonLinearMaxIterations,
                callback_post_solve = postSolve,
                )
            uw.libUnderworld.Underworld.AXequalsX(
                stokes._rot._cself,
                stokes._velocitySol._cself,
                False
                )

        def integrate():
            dt = courant * advDiff.get_max_dt()
            advDiff.integrate(dt)
            return dt

        super().__init__(locals(), **kwargs)

### ATTRIBUTES ###
CLASS = Viscoplastic
