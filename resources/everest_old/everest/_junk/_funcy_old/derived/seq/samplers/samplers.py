from .hypercube import Latin as _Latin
from .linear import Bifurcate as _Bifurcate

class Samplers:
    @classmethod
    def latin(cls, *args, **kwargs):
        return Sampler(_Latin, *args, **kwargs)
    @classmethod
    def bifurcate(cls, *args, **kwargs):
        return Sampler(_Bifurcate, *args, **kwargs)
class Sampler:
    def __init__(self, cls, *args, **kwargs):
        self.cls, self.args, self.kwargs = cls, args, kwargs
    def __call__(self, lBnd, uBnd):
        return self.cls(lBnd, uBnd, *self.args, **self.kwargs)