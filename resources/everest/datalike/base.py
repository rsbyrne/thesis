from everest.funcy.base import Function

from .exceptions import *

class Datalike(Function):
    def __init__(self, *args, name = None, **kwargs):
        if name is None:
            raise ValueError("Datalikes must be provided a 'name' kwarg")
    @property
    def semantics(self):
        return None
    @property
    def data(self):
        return self.value
