###############################################################################
'''The module defining the funcy 'Inc' ur type.'''
###############################################################################

from . import _utilities, _gruple

from .ur import Ur as _Ur

_unpacker_zip = _utilities.unpacker_zip

class Inc(_Ur):
    '''
    Wraps all funcy functions which are Slots
    or have at least one Slot term.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.openterms = _gruple.Gruple(
            t for t in self.terms if isinstance(t, Inc)
            )
        assert hasattr(self.wrapped, 'kwargs')
    def close(self, *args):
        wrapped = self.wrapped
        terms = (
            term.close(arg)
                for term, arg in _unpacker_zip(self.openterms, args)
            )
        return type(wrapped)(*terms, **wrapped.kwargs)
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Inc:
            if any('get_value' in B.__dict__ for B in C.__mro__):
                if any('close' in B.__dict__ for B in C.__mro__):
                    return True
        return NotImplemented

###############################################################################
###############################################################################
