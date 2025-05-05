###############################################################################
'''The module defining the 'Group' Derived type.'''
###############################################################################

from . import _abstract
from . import _gruple

from .derived import Derived as _Derived

class Group(_Derived):
    def evaluate(self, *terms):
        return _gruple.Gruple(iter(terms))
_ = _abstract.structures.Struct.register(_Derived)

###############################################################################
###############################################################################
