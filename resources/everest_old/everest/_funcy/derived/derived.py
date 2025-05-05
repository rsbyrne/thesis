###############################################################################
'''The module defining the parent class for all Derived types.'''
###############################################################################

from . import _Funcy, _ur, _abstract, _gruple

evaluable = _abstract.general.evaluable

class Derived(_Funcy):
    evaluate = lambda *_: None
    '''The parent class of all funcy 'instruments'.'''
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__init__(*args, **kwargs)
        return _ur.convert(obj)
    def __init__(self, *terms, **kwargs):
        terms = _gruple.Gruple(_ur.convert(t) for t in terms)
        kwargs = _gruple.GrupleMap(kwargs.items())
        self.terms, self.kwargs = terms, kwargs
        super().__init__(*terms, **kwargs)
    def __repr__(self):
        return f"{self.__class__.__name__}{self.kwargs}{self.terms}"
    def _resolve_terms(self):
        for term in self.terms:
            if evaluable(term):
                yield term.value
            else:
                yield term
    def get_value(self):
        return self.evaluate(*self._resolve_terms())

###############################################################################
###############################################################################
