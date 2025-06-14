from everest.datalike.datums.numerical.vector import Position

from .base import Flavour
from ..ptolemaic.frames import Traversable, Chronable

class Particles(Flavour, Traversable, Chronable):
    @classmethod
    def _stateVar_construct(cls):
        super()._stateVar_construct()
        class StateVar(cls.StateVar, Position):
            ...
        cls.StateVar = StateVar
        return
