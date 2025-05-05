###############################################################################
'''The module defining the funcy 'Var' ur type.'''
###############################################################################

from . import _utilities, _gruple

from .ur import Ur as _Ur

_unpacker_zip = _utilities.unpacker_zip

def get_terms(terms, key):
    return terms if key is None else terms[key]

class Var(_Ur):
    '''
    Wraps all funcy functions which are Variable
    or have at least one Variable term.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.varterms = _gruple.Gruple(
            t for t in self.terms if isinstance(t, Var)
            )
    def set_value(self, val, key = None, /):
        if val is None:
            self.del_value(key)
        else:
            zipped = _unpacker_zip(get_terms(self.varterms, key), val)
            for term, _val in zipped:
                term.set_value(_val)
    def del_value(self, key = None, /):
        for term in get_terms(self.varterms, key):
            term.del_value()
    def __setitem__(self, key, val, /):
        self.set_value(val, key)
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Var:
            if any('get_value' in B.__dict__ for B in C.__mro__):
                if any('set_value' in B.__dict__ for B in C.__mro__):
                    return True
        return NotImplemented

###############################################################################
###############################################################################
