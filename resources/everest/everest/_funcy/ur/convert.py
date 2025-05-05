###############################################################################
'''The module defining the constructor for all funcy 'ur' types.'''
###############################################################################

from . import _Funcy, _abstract

from .ur import Ur as _Ur
from .dat import Dat as _Dat
from .inc import Inc as _Inc
from .non import Non as _Non
from .seq import Seq as _Seq
from .var import Var as _Var

evaluable = _abstract.general.evaluable

def convert(obj: _Funcy):
    '''The constructor for all funcy 'ur' types.'''
    cls = None
    if isinstance(obj, _Funcy):
        if isinstance(obj, _Ur):
            return obj
        terms = None
        if isinstance(obj, tuple):
            terms = obj
        elif hasattr(obj, "terms"): # hence is Derived
            terms = obj.terms
        if not terms is None:
            if all(isinstance(t, _Non) for t in terms):
                cls = _Non
            elif any(isinstance(t, _Inc) for t in terms):
                cls = _Inc
            elif any(isinstance(t, _Var) for t in terms):
                cls = _Var
            elif any(isinstance(t, _Seq) for t in terms):
                cls = _Seq
            elif any(isinstance(t, _Dat) for t in terms):
                cls = _Dat
    elif isinstance(obj, _abstract.primitive.Primitive):
        cls = _Non
    if cls is None:
        raise TypeError(
            f"Couldn't convert object {obj} of type {type(obj)} to Ur type."
            )
    obj = cls(obj)
    if cls is _Non:
        return obj.value
    return obj

###############################################################################
###############################################################################
