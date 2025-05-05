from underworld.function._function import Function as UWFn

from . import _function
from . import _convert
from ._construct import _construct as _master_construct
from .. import utilities
from .. import meshutils

def _construct(*args, **kwargs):
    func = _master_construct(Vanilla, *args, **kwargs)
    return func

class Vanilla(_function.Function):

    opTag = 'Vanilla'

    def __init__(self, inVar, *args, varName = None, vector = None, **kwargs):

        var = UWFn.convert(inVar)

        if not hasattr(var, '_underlyingDataItems'):
            raise Exception
        if not len(var._underlyingDataItems) > 0:
            raise Exception

        self.defaultName = var.__hash__()
        self.varName = varName

        inVars = _convert.convert(
            tuple(
                sorted(
                    var._underlyingDataItems
                    )
                )
            )

        self.vector = vector

        self.stringVariants = {'varName': varName}
        self.inVars = inVars
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

    def _detect_substrates(self):
        self.mesh = utilities.get_mesh(self.var)
        self.meshUtils = meshutils.get_meshUtils(self.mesh)
        self.substrate = utilities.get_prioritySubstrate(self.var)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)
