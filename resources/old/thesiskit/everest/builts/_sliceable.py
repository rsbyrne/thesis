from functools import reduce

from . import Built
from ..exceptions import EverestException
from ..weaklist import WeakList

class SliceTypeError(EverestException):
    '''The object providing for slicing was of unexpected type.'''
    pass

class Sliceable(Built):
    def __init__(self, **kwargs):
        self._slice_fns = WeakList()
        super().__init__(**kwargs)
    def __getitem__(self, slicer):
        return reduce(
        lambda x, y: y(x),
        [slicer, *self._slice_fns]
        )
