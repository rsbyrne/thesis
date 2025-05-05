###############################################################################
''''''
###############################################################################

from .scalar import Scalar as _Scalar
from .array import Array as _Array
from .misc import Misc as _Misc
from .variable import Variable as _Variable

from .exceptions import *

def construct_variable(arg = None, /, *args, **kwargs) -> _Variable:
    es = []
    for kind in (_Array, _Scalar, _Misc):
        try:
            return kind._construct(arg, *args, **kwargs)
        except VariableConstructFailure as e:
            es.append(e)
    raise VariableConstructFailure(
        "Variable construct failed"
        f" with args = {(arg, *args)}, kwargs = {kwargs};"
        f" {tuple(es)}"
        )

###############################################################################
''''''
###############################################################################