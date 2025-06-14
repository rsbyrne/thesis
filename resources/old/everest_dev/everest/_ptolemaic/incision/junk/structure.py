###############################################################################
''''''
###############################################################################


import operator as _operator

from . import _utilities

from .sett import Sett as _Sett

_Diskable = _utilities.classtools.Diskable


@_Diskable
class Operation:

    __slots__ = ('operator', 'args', *_Diskable.reqslots)

    def __init__(self, operator, /, *args):
        self.operator = operator
        self.args = args
        self.register_argskwargs(operator, *args)


@_Diskable
class Operator:

    __slots__ = ('inchoras', 'outchora', *_Diskable.reqslots)

    def __init__(self, /, *choras):
        self.inchoras, self.outchora = choras[:-1], choras[-1]
        self.register_argskwargs(*choras)

    def __call__(self, *args):
        if not all(map(_operator.contains, self.inchoras, args)):
            raise ValueError(args)
        return Operation(self, *args)


class Structure(_Sett):

    @classmethod
    def parameterise(cls, register, /, *choras, **operators):
        register(*choras, **operators)
        super().parameterise(register)

    def __init__(self, chora0, *choras, **operators):
        self.chora0, self.choras, self.operators = chora0, choras, operators
        super().__init__()

    @property
    def __contains__(self):
        return self.chora0.__contains__


###############################################################################
###############################################################################
