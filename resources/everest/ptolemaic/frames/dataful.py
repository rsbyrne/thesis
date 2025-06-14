from everest.datalike.base import Datalike as _Datalike
from everest.datalike.structures import \
    Ensemble as _Ensemble, \
    Magazine as _Magazine, \
    Assembly as _Assembly
from everest.datalike.datums import Datum as _Datum

from .base import Frame

class Dataful(Frame):

    @classmethod
    def _datafulclass_construct(cls):
        class DatafulClass(_Datalike):
            ...
        cls.DatafulClass = DatafulClass
        return

    @classmethod
    def _dataclass_construct(cls):
        class Ensemble(_Ensemble, cls.DatafulClass):
            ...
        class Magazine(_Magazine, cls.DatafulClass):
            ...
        class Assembly(_Assembly, cls.DatafulClass):
            ...
        class Datum(_Datum, cls.DatafulClass):
            ...
        cls.Ensemble = Ensemble
        cls.Magazine = Magazine
        cls.Assembly = Assembly
        cls.Datum = Datum
        return

    @classmethod
    def _class_construct(cls):
        super()._class_construct()
        cls._datafulclass_construct()
        cls._dataclass_construct()
        return

    def __init__(self,
            _outVars = None,
            **kwargs,
            ):
        outVars = [] if _outVars is None else _outVars
        self.data = self.Assembly(outVars)
        super().__init__(**kwargs)
