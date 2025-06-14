from .base import Real
from .exceptions import *

class Spatial(Real):
    @property
    def dim(self):
        raise MissingAsset

class Linear(Spatial):
    @property
    def dim(self):
        return 1

class Planar(Spatial):
    @property
    def dim(self):
        return 2

class Volar(Spatial):
    @property
    def dim(self):
        return 3
