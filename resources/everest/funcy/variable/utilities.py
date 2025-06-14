    # from .base import Variable
    # from .number import Number

def construct_variable(*args, stack = False, **kwargs):
    from .scalar import Scalar
    from .array import Array
    from .stack import Stack
    if stack:
        return Stack(*args, **kwargs)
    totry = Scalar, Array
    for kind in totry:
        try:
            return kind(*args, **kwargs)
        except TypeError:
            pass
    raise TypeError

from ..utilities import ordered_unpack
