###############################################################################
''''''
###############################################################################


import functools as _functools
import itertools as _itertools

from . import _utilities

from .base import AlgebraInstance as _AlgebraInstance
from .sett import Sett as _Sett  #, Element as _Element
from .operation import Operation as _Operation


class AlgebraOperator(_AlgebraInstance):

    def __init__(self, operator, *inputs):
        self.operator = operator
        self.valence = operator.valence
        self.inputs = inputs
        if not len(inputs) == operator.valence:
            raise TypeError("Arity mismatch!")

    def unpack_arg(self, dest, arg, source):
        arg = (dest if source is None else source)[arg]
        if isinstance(name := arg.name, _Operation):
            return name
        return arg

    def __call__(self, *args, dest: _Sett, **kwargs):
        unpacker = _functools.partial(self.unpack_arg, dest)
        return dest[
            self.operator(
                *map(unpacker, args, self.inputs),
                **kwargs,
                )
            ]

    def _repr(self):
        return self.operator._cls_repr()


class Algebra(_Sett):

    def dest_wrap(self, op):

        if not isinstance(op, AlgebraOperator):
            op = AlgebraOperator(op, *_itertools.repeat(None, op.valence))

        @_functools.wraps(op)
        def wrapper(*args, **kwargs):
            return op(*args, dest=self, **kwargs)

        return wrapper

    def get_element_namespace(self):
        operations = {
            key: self.dest_wrap(val)
            for key, val in self.operations.items()
            }
        return super().get_element_namespace() | operations

    def split_op_con(self, **kwargs):
        constants, operations = dict(), dict()
        for name, op in kwargs.items():
            if op.valence:
                operations[name] = op
            else:
                constants[name] = op
        return constants, operations

    def __init__(self, name, /, *args, **operations):
        self.constants, self.operations = self.split_op_con(**operations)
        super().__init__(
            name,
            _utilities.Criterion.Union(_Operation, list(args))
            )
        for key, val in self.constants.items():
            setattr(self.Element, key, self[val()])

    def _repr(self):
        return f"{repr(self.name)}, operations={self.operations}"


###############################################################################
###############################################################################
