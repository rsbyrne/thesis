import underworld as uw
fn, cd = uw.function, uw.conditions

from . import _convert
from . import _function
from ._construct import _construct as _master_construct
from . import component as _component
from . import gradient as _gradient
from . import _constant

def _construct(*args, **kwargs):
    func = _master_construct(Conduction, *args, **kwargs)
    return func

class Conduction(_function.Function):

    opTag = 'Conduction'

    def __init__(self,
            temperatureField,
            HFn,
            diffFn,
            *args,
            fluxType = 'None',
            **kwargs
            ):

        inVars = []
        temperatureField = _convert.convert(temperatureField)
        HFn = _convert.convert(HFn)
        diffFn = _convert.convert(diffFn)
        inVars = [temperatureField, HFn, diffFn]

        if len(args) == 2:
            raise Exception("Doesn't work yet!")
            innerFluxFn = _convert.convert(args[0])
            outerFluxFn = _convert.convert(args[1])
            inVars.extend([innerFluxFn, outerFluxFn])
        elif len(args) == 1:
            if fluxType == 'outer':
                innerFluxFn = None
                outerFluxFn = _convert.convert(args[0])
                inVars.append(outerFluxFn)
            elif fluxType == 'inner':
                outerFluxFn = None
                innerFluxFn = _convert.convert(args[0])
                inVars.append(innerFluxFn)
            else:
                raise ValueError
        else:
            innerFluxFn = outerFluxFn = None

        mesh = temperatureField.mesh

        conductionField = mesh.add_variable(1)
        inner, outer = mesh.specialSets['inner'], mesh.specialSets['outer']
        if innerFluxFn is None and outerFluxFn is None:
            conductionField.data[outer] = temperatureField.var.data[outer]
            conductionField.data[inner] = temperatureField.var.data[inner]
            condBC = cd.DirichletCondition(conductionField, (inner + outer,))
            condBCs = [condBC,]
        elif outerFluxFn is None:
            conductionField.data[outer] = temperatureField.var.data[outer]
            condBC = cd.DirichletCondition(conductionField, (outer,))
            condFluxBC = cd.NeumannCondition(
                conductionField, (inner,), innerFluxFn
                )
            condBCs = [condBC, condFluxBC]
        elif innerFluxFn is None:
            conductionField.data[inner] = temperatureField.var.data[inner]
            condBC = cd.DirichletCondition(conductionField, (inner,))
            condFluxBC = cd.NeumannCondition(
                conductionField, (outer,), outerFluxFn
                )
            condBCs = [condBC, condFluxBC]
        else:
            conductionField.data[:] = 0.
            condFluxBC1 = cd.NeumannCondition(
                conductionField, (inner,), innerFluxFn
                )
            condFluxBC2 = cd.NeumannCondition(
                conductionField, (outer,), outerFluxFn
                )
            condBCs = [condFluxBC1, condFluxBC2]

        conductive = uw.systems.SteadyStateHeat(
            temperatureField = conductionField,
            fn_diffusivity = diffFn,
            fn_heating = HFn,
            conditions = condBCs
            )
        conductiveSolver = uw.systems.Solver(conductive)

        self.solver = conductiveSolver
        self.condBCs = condBCs

        self.stringVariants = {'fluxType': fluxType}
        self.inVars = inVars
        self.parameters = []
        self.var = conductionField

        super().__init__(**kwargs)

    def _partial_update(self):
        self.solver.solve()

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def inner(*args, **kwargs):
    return _construct(*args, fluxType = 'inner', **kwargs)

def outer(*args, **kwargs):
    return _construct(*args, fluxType = 'outer', **kwargs)

def dual(*args, fluxType = 'both', **kwargs):
    return _construct(*args, **kwargs)
