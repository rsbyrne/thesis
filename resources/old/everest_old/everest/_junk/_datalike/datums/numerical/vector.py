###############################################################################
''''''
###############################################################################
from .array import Array
from .exceptions import *

class Vector(Array):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.shape) > 1:
            raise DatalikeValueError("Not a vector.")
        self.dim = self.shape[0]

class Position(Vector):
    from ...semantics.spacelike import Spacelike as semantic

###############################################################################
''''''
###############################################################################
