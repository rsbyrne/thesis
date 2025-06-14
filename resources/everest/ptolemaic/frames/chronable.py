import numbers
import numpy as np

from everest.datalike.qualifieds.indexed import Chroned
from everest.datalike.datums.numerical.scalar import Chron

from .indexable import Indexable

class Chronable(Indexable):

    @classmethod
    def _datafulclass_construct(cls):
        class DatafulClass(cls.DatafulClass, Chroned):
            ...
        cls.DatafulClass = DatafulClass
        return

    @classmethod
    def _chronVar_construct(cls):
        class ChronVar(Chron, cls.IndexVar):
            ...
        cls.ChronVar = ChronVar
        return

    @classmethod
    def _class_construct(cls):
        super()._class_construct()
        cls._chronVar_construct()
        return

    def __init__(self,
            _indices = None,
            **kwargs
            ):
        _indices = [] if _indices is None else _indices
        var = self.ChronVar()
        _indices.append(var)
        super().__init__(
            _indices = _indices,
            **kwargs
            )
