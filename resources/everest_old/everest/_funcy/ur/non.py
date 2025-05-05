###############################################################################
'''The module defining the funcy 'Non' ur type.'''
###############################################################################

from . import _abstract

from .ur import Ur as _Ur

class Non(_Ur):
    '''
    Wraps all funcy functions which are Primitive
    or have at least one Primitive term.
    '''
_ = Non.register(_abstract.primitive.Primitive)

###############################################################################
###############################################################################
