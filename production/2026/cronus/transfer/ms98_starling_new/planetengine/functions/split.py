from . import _function
from . import _convert
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Split, *args, **kwargs)
    return func

class Split(_function.Function):

    opTag = 'Split'

    def __init__(self, inVar, *args, column = 0, **kwargs):

        inVar = _convert.convert(inVar)

        if not inVar.varDim > 1:
            raise Exception
        if inVar.substrate is None:
            raise Exception

        if inVar.meshbased:
            var = inVar.substrate.add_variable(
                1,
                inVar.dType
                )
        else:
            var = inVar.substrate.add_variable(
                inVar.dType,
                1
                )

        self.column = column

        self.stringVariants = {'column': str(column)}
        self.inVars = [inVar]
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

    def _partial_update(self):
        self.var.data[:, 0] = \
            self.inVar.data[:, self.column]

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def getall(inVar):
    inVar = _convert.convert(inVar)
    returnVars = []
    for dim in range(inVar.varDim):
        returnVars.append(_construct(inVar, column = dim))
    return tuple(returnVars)
