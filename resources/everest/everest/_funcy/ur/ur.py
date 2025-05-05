###############################################################################
'''Defines the parent class of all funcy 'ur' types.'''
###############################################################################

from . import _Funcy

class Ur(_Funcy):
    '''The parent class of all funcy 'ur' types.'''
    def __init__(self, wrapped, /, *args, **kwargs):
        self.wrapped = wrapped
        self.terms = wrapped.terms
        super().__init__(wrapped, *args, **kwargs)
    def get_value(self):
        return self.wrapped.get_value()
    def __repr__(self):
        return f"{self.__class__.__name__}_{repr(self.wrapped)}"
    def __reduce__(self):
        return self.wrapped.__reduce__()
    # @classmethod
    # def __subclasshook__(cls, C):
    #     if cls is Ur:
    #         if any('get_value' in B.__dict__ for B in C.__mro__):
    #             if not any('evaluate' in B.__dict__ for B in C.__mro__):
    #                 return True
    #     return NotImplemented

###############################################################################
###############################################################################
