###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC

class AbstractDimension(_ABC):
    ...

class Typed(AbstractDimension):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Typed:
            if any("typ" in B.__dict__ for B in C.__mro__):
                return True
            if any("__slots__" in B.__dict__ for B in C.__mro__):
                if 'typ' in C.__slots__:
                    return True
        return NotImplemented


###############################################################################
###############################################################################
