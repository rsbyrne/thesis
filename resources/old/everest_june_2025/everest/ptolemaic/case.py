###############################################################################
''''''
###############################################################################

from . import _reseed
from .schema import Schema as _Schema

class Case(_Schema):
    def __call__(cls, *args, **kwargs):
        if hasattr(cls, 'process_inputs'):
            args, kwargs = cls.process_inputs(args, kwargs)
        inputs = cls.inputs.bind(*args, **kwargs)
        inst = super().__call__(*inputs.args, **inputs.kwargs)
        inst.hashID = cls.hashID + ';' + str(_reseed.rdigits(12))
        inst.Case = cls
        return inst

###############################################################################
###############################################################################
