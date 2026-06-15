from . import _function
from . import _convert
from . import _basetypes
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Rebase, *args, **kwargs)
    return func

class Rebase(_function.Function):

    opTag = 'Rebase'

    def __init__(self, inVar, refVar, *args, **kwargs):

        inVar, refVar = inVars = _convert.convert(inVar, refVar)

        self.refVar = refVar

        self.stringVariants = {}
        self.inVars = list(inVars)
        self.parameters = []
        self.var = inVar.var

        super().__init__(**kwargs)

    def _scaleFn(self):
        scales = [self.min, self.max]
        ref = self.refVar.data
        outs = []
        difference = max([abs(x - ref) for x in scales])
        return [ref - difference, ref + difference]

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def zero(baseVar, *args, **kwargs):
    return _construct(baseVar, 0., **kwargs)
