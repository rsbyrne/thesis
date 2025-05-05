import numpy as np

from . import _convert
from . import _reduction
from . import _basetypes
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Fourier, *args, **kwargs)
    return func

class Fourier(_reduction.Reduction):

    opTag = 'Fourier'

    def __init__(self, inVar, *args, **kwargs):

        inVar = _convert.convert(inVar)

        if not isinstance(inVar, _reduction.Reduction):
            raise Exception

        def evalFn():
            data = inVar.data
            av = np.average(data)
            norm = (data - av) / av
            sp = np.abs(np.fft.rfft(norm)).real
            freq = np.fft.rfftfreq(norm.size, 1. / (2. * sp.size))
            domFreq = int(round(max(zip(sp, freq))[1]))
            return domFreq
        var = _basetypes.Parameter(evalFn)

        self.stringVariants = {}
        self.inVars = [inVar]
        self.parameters = [var]
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)
