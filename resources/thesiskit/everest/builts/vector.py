import numpy as np
import operator

from . import Built

class Vector(Built):
    _swapscript = '''from everest.builts.vector import Vector as CLASS'''
    def __init__(self, **kwargs):
        self.keys = sorted(kwargs.keys())
        self.vals = [kwargs[key] for key in self.keys]
        self.data = np.array(self.vals)
        super().__init__()
    def __iter__(self):
        for key, inp in sorted(self.inputs.items()):
            yield (key, inp)
    def __len__(self):
        return len(self.inputs)
    def __getitem__(self, key):
        return self.inputs[key]
    def __contains__(self, key):
        return key in self.keys
    def __array__(self):
        return self.data
    def _operation(self, arg, opFn):
        if isinstance(arg, Vector):
            mod1 = {**arg.inputs, **self.inputs}
            mod2 = {**self.inputs, **arg.inputs}
            return [opFn(mod1[key], mod2[key]) for key in mod1]
        else:
            raise TypeError
    # def __eq__(self, arg): return self._operation(arg, operator.eq)
    # def __gt__(self, arg): return self._operation(arg, operator.gt)
    # def __lt__(self, arg): return self._operation(arg, operator.lt)
    # def __ge__(self, arg): return self._operation(arg, operator.ge)
    # def __le__(self, arg): return self._operation(arg, operator.eq)
