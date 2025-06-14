###############################################################################
''''''
###############################################################################

from . import _generic
from .derived import Derived as _Derived

from .exceptions import *

class Slyce(_Derived, _generic.Slice):

    def __init__(self, arg1, arg2 = None, arg3 = None, /, **kwargs):
        super().__init__(arg1, arg2, arg3)

    def _evaluate(self, terms):
        return slice(*terms)

###############################################################################
''''''
###############################################################################