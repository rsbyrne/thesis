###############################################################################
''''''
###############################################################################
import numbers

import numpy as np

from everest.funcy.base.variable import Scalar as FnScalar

from .base import Continuous, Discrete

class Scalar(FnScalar):
    __slots__ = ('compType')
    def __init__(self, *args, compType = numbers.Number, **kwargs):
        self.compType = compType
        super().__init__(*args, **kwargs)

class Real(Scalar, Continuous):
    def __init__(self,
            *args,
            compType = numbers.Real,
            dtype = np.float32,
            **kwargs
            ):
        super().__init__(*args, compType = compType, dtype = dtype, **kwargs)

class Integral(Real, Discrete):
    def __init__(self,
            *args,
            compType = numbers.Integral,
            dtype = np.int32,
            **kwargs
            ):
        super().__init__(*args, compType = compType, dtype = dtype, **kwargs)

correspondences = {
    numbers.Integral : Integral,
    numbers.Real : Real,
    }

###############################################################################
''''''
###############################################################################
