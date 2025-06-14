###############################################################################
''''''
###############################################################################

from ..exceptions import BythicException, NotYetImplemented


class DimensionException(BythicException):
    '''Base class for special exceptions raised by Dimension classes.'''
class DimensionUniterable(DimensionException):
    '''This dimension cannot be iterated over.'''
class DimensionInfinite(DimensionException):
    '''This dimension is infinitely long.'''

###############################################################################
###############################################################################
