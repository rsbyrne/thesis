from .exceptions import *
from ..nested import Nested
from .spatial import Spatial, Linear, Planar, Volar

class Tensor(Spatial, Nested):
    @property
    def depth(self):
        return 2
    @property
    def subtype(self):
        raise MissingAsset

class VectorFilled(Tensor):
    ...
class ScalitoFilled(VectorFilled):
    from .vector import Scalito
    @property
    def subtype(self):
        return Scalito
class PlanitoFilled(VectorFilled):
    from .vector import Planito
    @property
    def subtype(self):
        return Planito
class VolitoFilled(VectorFilled):
    from .vector import Volito
    @property
    def subtype(self):
        return Volito

class Stack(Linear, Tensor):
    ...
class ScalarStack(Stack, ScalitoFilled):
    ...
class PlanarStack(Stack, PlanitoFilled):
    ...
class VolarStack(Stack, VolitoFilled):
    ...

class Field(Planar, Tensor):
    ...
class ScalarField(Field, ScalitoFilled):
    ...
class PlanarField(Field, PlanitoFilled):
    ...
class VolarField(Field, VolitoFilled):
    ...

class Space(Volar, Tensor):
    ...
class ScalarSpace(Space, ScalitoFilled):
    ...
class PlanarSpace(Space, PlanitoFilled):
    ...
class VolarSpace(Space, VolitoFilled):
    ...
