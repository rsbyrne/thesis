###############################################################################
'''The module describing the 'primitive' types understood by funcy.'''
###############################################################################

from . import _special

from .abstract import EverestABC as _EverestABC

PRIMITIVETYPES = set((
    int,
    float,
    complex,
    str,
    type(None),
    tuple,
    _special.Empty,
    ))

class Primitive(_EverestABC):
    '''The virtual superclass of all acceptable funcy primitive types.'''
for typ in PRIMITIVETYPES:
    _ = Primitive.register(typ)

###############################################################################
###############################################################################
