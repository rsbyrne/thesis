from .base import Variable
from ..special import null
from .exceptions import *

class Number(Variable):

    __slots__ = (
        'shape',
        'dtype',
        )

    def __init__(self, shape = (), dtype = None, /, *args, **kwargs):
        self.shape, self.dtype = shape, dtype
        super().__init__(shape, dtype, *args, **kwargs)

    def nullify(self):
        self.memory = null
        self.refresh()
    @property
    def isnull(self):
        return self.memory is null

    def __iadd__(self, arg):
        self.memory += arg
        self.refresh()
        return self
    def __isub__(self, arg):
        self.memory -= arg
        self.refresh()
        return self
    def __imul__(self, arg):
        self.memory *= arg
        self.refresh()
        return self
    def __itruediv__(self, arg):
        self.memory /= arg
        self.refresh()
        return self
    def __ifloordiv__(self, arg):
        self.memory //= arg
        self.refresh()
        return self
    def __imod__(self, arg):
        self.memory %= arg
        self.refresh()
        return self
    def __ipow__(self, arg):
        self.memory **= arg
        self.refresh()
        return self
