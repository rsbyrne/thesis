###############################################################################
''''''
###############################################################################


from . import _misc

from .adderclass import AdderClass as _AdderClass
from .hashidable import HashIDable as _HashIDable

_FrozenMap = _misc.FrozenMap


@_HashIDable
class Registrar:

    __slots__ = (
        '_args', '_kwargs', '_argtup', '_frozenkwargs', '_argskwargslocked',
        *_HashIDable.reqslots
        )

    def __init__(self, /):
        self._argskwargslocked = False
        self._args = []
        self._kwargs = {}

    @property
    def argskwargslocked(self):
        return self._argskwargslocked

    def register(self, *args, **kwargs):
        if self.argskwargslocked:
            raise RuntimeError("Cannot register on frozen registrar.")
        for att in ('_argtup', '_frozenkwargs'):
            if hasattr(self, att):
                delattr(self, att)
        self._args.extend(args)
        self._kwargs.update(kwargs)

    def freeze(self):
        self._argskwargslocked = True

    @property
    def args(self):
        try:
            return self._argtup
        except AttributeError:
            argtup = self._argtup = tuple(self._args)
            self.freeze()
            return argtup

    @property
    def kwargs(self):
        try:
            return self._frozenkwargs
        except AttributeError:
            fkw = self._frozenkwargs = _FrozenMap(**self._kwargs)
            self.freeze()
            return fkw

    def get_hashcontent(self):
        return self.args, self.kwargs

    def __call__(self, *args, **kwargs):
        return self.register(*args, **kwargs)


def master_unreduce(constructor, args, kwargs):
    if isinstance(constructor, tuple):
        constructor, *names = constructor
        for name in names:
            constructor = getattr(constructor, name)
    return constructor(*args, **dict(kwargs))


class Reloadable(_AdderClass):

    reqslots = ('_registrar',)

    @_AdderClass.decorate(property)
    def registrar(self):
        try:
            return self._registrar
        except AttributeError:
            registrar = self._registrar = Registrar()
            return registrar

    @_AdderClass.decorate(property)
    def freeze_argskwargs(self):
        return self.registrar.freeze()

    @_AdderClass.decorate(property)
    def register_argskwargs(self):
        return self.registrar.register

    @_AdderClass.decorate(property)
    def args(self):
        return self.registrar.args

    @_AdderClass.decorate(property)
    def kwargs(self):
        return self.registrar.kwargs

    @_AdderClass.decorate(classmethod)
    def get_constructor(cls):  # pylint: disable=E0213
        if hasattr(cls, 'constructor'):
            return cls.constructor  # pylint: disable=E1101
        if hasattr(cls, 'classpath'):
            return cls.classpath  # pylint: disable=E1101
        if hasattr(cls, 'get_classpath'):
            return cls.get_classpath()
        return cls

    @_AdderClass.decorate(property)
    def unreduce(self):  # pylint: disable=R0201
        return master_unreduce

    @_AdderClass.forcemethod
    def __reduce__(self):
        return self.unreduce, self.get_redtup()

    def get_redtup(self):
        return self.get_constructor(), self.args, self.kwargs

    def copy(self):
        unredfn, args = self.__reduce__()
        return unredfn(*args)  # pylint: disable=E1121


###############################################################################
###############################################################################
