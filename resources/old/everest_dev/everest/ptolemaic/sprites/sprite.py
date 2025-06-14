###############################################################################
''''''
###############################################################################


from . import _Ptolemaic, _Primitive

from . import exceptions as _exceptions


class BadParameter(_Ptolemaic.BadParameter, _exceptions.SpriteException):

    def message(self, /):
        yield from super().message()
        yield ' '.join((
            "Note that only Primitive types (e.g. `int`, `float`)",
            "are accepted as parameters of `Sprite` subclasses.",
            ))


class Sprite(_Ptolemaic):
    '''
    The base class for all 'sprites',
    or classes whose inputs are restricted to being Primitive.
    '''

    BadParameter = BadParameter

    @classmethod
    def check_param(cls, arg):
        if isinstance(arg, _Primitive):
            return arg
        raise cls.BadParameter(arg)


###############################################################################
###############################################################################
