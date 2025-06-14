###############################################################################
'''The module defining the top-level 'incisor' types.'''
###############################################################################

from . import _abstract
_EverestABC = _abstract.abstract.EverestABC
_datalike = _abstract.datalike
_general = _abstract.general
_structures = _abstract.structures

class Incisor(_EverestABC):
    ...

class TrivialIncisor(Incisor):
    def __repr__(self):
        return 'trivial'
trivial = TrivialIncisor()

class ShallowIncisor(Incisor):
    ...

class StrictIncisor(ShallowIncisor):
    ...
_ = StrictIncisor.register(_datalike.Integral)
_ = StrictIncisor.register(_datalike.String)
_ = StrictIncisor.register(_structures.Mapping)

class SoftIncisor(ShallowIncisor):
    ...
_ = SoftIncisor.register(_general.Slice)

class BroadIncisor(SoftIncisor):
    ...
_ = BroadIncisor.register(_structures.Unpackable)

class DeepIncisor(Incisor):
    ...
_ = DeepIncisor.register(_structures.Struct)
_ = DeepIncisor.register(type(Ellipsis))

class SubIncisor(DeepIncisor):
    ...
subinc = SubIncisor()

###############################################################################
###############################################################################
