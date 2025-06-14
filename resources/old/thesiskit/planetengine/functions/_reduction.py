import numpy as np

from . import _planetvar

class Reduction(_planetvar.PlanetVar):

    def __init__(self, *args, **kwargs):

        self.mesh = self.substrate = None

        sample_data = self.var.evaluate()
        self.dType = _planetvar.get_dType(sample_data)
        self.varType = 'red'
        self.meshUtils = None
        self.meshbased = False

        self._hashVars = self.inVars

        super().__init__(**kwargs)

    def _output_processing(self, evalOutput):
        val = evalOutput.flatten()
        if len(val) == 1: return val[0]
        else: return val
