###############################################################################
''''''
###############################################################################

from . import _generic
from .derived import Derived as _Derived

from .exceptions import *

class UnSeq(_Derived, _generic.Sequence):

    def __init__(self, seq, **kwargs):
        super().__init__(seq, **kwargs)

    def _evaluate(self):
        return list(self.prime.value)

###############################################################################
''''''
###############################################################################
