import random
import numpy as np

import underworld as uw
fn = uw.function
UWFn = fn._function.Function

from . import _basetypes
from . import _planetvar

class Parameter(_basetypes.BaseTypes):

    opTag = 'Parameter'

    def __init__(self, inFn, **kwargs):

        initialVal = inFn()
        var = fn.misc.constant(initialVal)
        if not len(list(var._underlyingDataItems)) == 0:
            raise Exception

        self._hashVars = []
        self.stringVariants = {}
        self.inVars = []
        self.parameters = []
        self.var = var
        self.mesh = self.substrate = None

        self._paramfunc = inFn
        self._hashval = random.randint(1, 1e18)

        self._update_attributes()
        sample_data = np.array([[val,] for val in self.value])
        self.dType = _planetvar.get_dType(sample_data)

        super().__init__(**kwargs)

    def _check_hash(self, **kwargs):
        return random.randint(0, 1e18)

    def _output_processing(self, evalOutput):
        val = evalOutput.flatten()
        if len(val) == 1: return val[0]
        else: return val

    def _update_attributes(self):
        self.value = self.var.evaluate()

    def _partial_update(self):
        self.var.value = self._paramfunc()
        self._update_attributes()

    def __hash__(self):
        return hash((_planetvar._PLANETVAR_FLAG, self.opTag, self._hashval))
