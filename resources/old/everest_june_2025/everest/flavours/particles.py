###############################################################################
''''''
###############################################################################
# from ..datalike.datums.numerical.vector import Position
from ..funcy.base.variable import Array

from .base import Flavour
from ..ptolemaic.frames import Traversable, Chronable

class Particles(Flavour, Traversable, Chronable):
    @classmethod
    def _stateVar_construct(cls):
        super()._stateVar_construct()
        class StateVar(cls.StateVar, Array):
            _defaultdtype = float
#             @classmethod
#             def _construct(cls, *args, dtype = float, **kwargs):
#                 super().__init__()
        cls.StateVar = StateVar
###############################################################################
''''''
###############################################################################
