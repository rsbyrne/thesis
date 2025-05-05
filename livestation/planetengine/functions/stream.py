import underworld as uw
fn, cd = uw.function, uw.conditions

from . import _convert
from . import _function
from ._construct import _construct as _master_construct
from . import component as _component
from . import gradient as _gradient

def _construct(*args, **kwargs):
    func = _master_construct(Stream, *args, **kwargs)
    return func

class Stream(_function.Function):

    opTag = 'Stream'

    def __init__(self, inVar, *args, **kwargs):

        inVar = _convert.convert(inVar)

        psiField = inVar.mesh.add_variable(1)
        periodic = any(inVar.mesh.periodic)
        if periodic: walls = inVar.meshUtils.surfaces['rad']
        else: walls = inVar.meshUtils.surfaces['all']
        psiBC = cd.DirichletCondition(psiField, walls)
        psiBCs = [psiBC,]
        psiField.data[:] = 0.

        # vel = inVar.var
        vel = inVar
        udy = _gradient.y(_component.x(vel))
        vdx = _gradient.x(_component.y(vel))
        # velDif = udy - vdx
        velDif = vdx - udy
        inVar = velDif

        psiSystem = uw.systems.SteadyStateHeat(
            temperatureField = psiField,
            fn_diffusivity = 1.,
            fn_heating = velDif,
            conditions = psiBCs
            )
        psiSolver = uw.systems.Solver(psiSystem)

        # For some really weird reason,
        # crashes without this here:
        self.psiBCs = psiBCs

        self.psiSolver = psiSolver

        # self.v

        self.stringVariants = {'periodic': str(periodic)}
        self.inVars = [inVar]
        self.parameters = []
        self.var = psiField

        super().__init__(**kwargs)

    def _partial_update(self):
        self.psiSolver.solve()

def default(*args, **kwargs):
    return _construct(*args, **kwargs)
