import numpy as np

import underworld as uw
fn = uw.function
UWFn = fn._function.Function

from . import _basetypes
from . import _planetvar

class Constant(_basetypes.BaseTypes):

    opTag = 'Constant'

    def __init__(self, inVar, *args, **kwargs):

        var = UWFn.convert(inVar)
        if var is None:
            raise Exception
        if len(list(var._underlyingDataItems)) > 0:
            raise Exception

        self.value = var.evaluate()[0]
        self._hashVars = [var]
        # self.data = np.array([[val,] for val in self.value])

        sample_data = np.array([[val,] for val in self.value])
        self.dType = _planetvar.get_dType(sample_data)
        self.varType = 'const'

        self.stringVariants = {'val': str(self.value)}
        self.inVars = []
        self.parameters = []
        self.var = var
        self.mesh = self.substrate = None
        self.meshUtils = None
        self.meshbased = False

        super().__init__(**kwargs)

    def _check_hash(self, **kwargs):
        return hash((_planetvar._PLANETVAR_FLAG, self.opTag, str(self.value)))

    def _output_processing(self, evalOutput):
        val = evalOutput.flatten()
        if len(val) == 1: return val[0]
        else: return val
