###############################################################################
''''''
###############################################################################

from numbers import Number as _Number

from .dat import Dat as _Dat, QuickDat as _QuickDat

class Quantity(_Dat):
    ...

class QuickQuantity(_QuickDat, Quantity):
    def __init__(self, value: _Number, /, **kwargs) -> None:
        super().__init__(value, **kwargs)

###############################################################################
''''''
###############################################################################