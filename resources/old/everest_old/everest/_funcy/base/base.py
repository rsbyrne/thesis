###############################################################################
'''The module defining the parent class for all Base types.'''
###############################################################################

from . import _Funcy, _reseed

class Base(_Funcy):
    @classmethod
    def _process_args(cls, *args):
        ...
    @classmethod
    def _process_kwargs(cls, name = None, **kwargs):
        if name is None:
            name = f"anon_{_reseed.rint(1e11, 1e12 - 1)}"
        kwargs['name'] = name
        return super()._process_kwargs(**kwargs)

###############################################################################
###############################################################################
