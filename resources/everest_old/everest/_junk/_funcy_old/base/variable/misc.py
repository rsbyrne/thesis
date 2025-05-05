###############################################################################
''''''
###############################################################################

from .variable import Variable as _Variable

from .exceptions import *
class MiscConstructFailure(VariableConstructFailure):
    ...

class Misc(_Variable):

    @classmethod
    def _construct(cls,
            arg: object = None,
            /, *args, **kwargs
            ) -> _Variable:
        if len(args):
            raise MiscConstructFailure(
                "Cannot pass multiple args to misc constructor"
                )
        if arg is object:
            if 'dtype' in kwargs:
                raise MiscConstructFailure("Multiple arguments for dtype.")
            else:
                kwargs['dtype'] = arg
        else:
            if 'initVal' in kwargs:
                raise MiscConstructFailure("Multiple arguments for initVal.")
            else:
                kwargs['initVal'] = arg
        if 'dtype' in kwargs:
            if (dtype := kwargs['dtype']) is object:
                return cls(**kwargs)
            else:
                raise MiscConstructFailure(
                    f"Provided dtype '{dtype}' not an acceptable type"
                    " for scalar constructor."
                    )
        else:
            raise MiscConstructFailure("No dtype provided.")

    def __init__(self, dtype = object, **kwargs):\
        super().__init__(dtype = str(dtype), **kwargs)

    def rectify(self):
        ...
    def set_value(self, val):
        self.memory = val

###############################################################################
''''''
###############################################################################
