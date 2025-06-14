from functools import cached_property

from everest.funcy.variable import Array as FnArray

from .scalar import correspondences
from .base import Numerical

class Array(Numerical, FnArray):
    @cached_property
    def elementType(self):
        dtype = self.dtype
        for abc in correspondences.keys():
            if issubclass(dtype, abc):
                return correspondences[abc]
        raise TypeError(dtype)
