###############################################################################
''''''
###############################################################################


from . import _misc

from .adderclass import AdderClass as _AdderClass

FrozenMap = _misc.FrozenMap


def master_unreduce(constructor, args, kwargs):
    if isinstance(constructor, tuple):
        constructor, *names = constructor
        for name in names:
            constructor = getattr(constructor, name)
    return constructor(*args, **dict(kwargs))


class Reloadable(_AdderClass):

    reqslots = ('_args', '_kwargs', '_frozenkwargs')

    def register_argskwargs(self, *args, **kwargs):
        try:
            _args = self._args
        except AttributeError:
            _args = self._args = list()  # pylint: disable=W0201
        try:
            _kwargs = self._kwargs
        except AttributeError:
            _kwargs = self._kwargs = dict()  # pylint: disable=W0201
        _args.extend(args)
        _kwargs.update(kwargs)

    @_AdderClass.decorate(property)
    def args(self):
        try:
            return tuple(self._args)
        except AttributeError:
            _args = self._args = tuple()  # pylint: disable=W0201
            return _args

    @_AdderClass.decorate(property)
    def kwargs(self):
        try:
            return self._frozenkwargs
        except AttributeError:
            try:
                kwargs = self._kwargs
            except AttributeError:
                kwargs = dict()
            frkw = self._frozenkwargs = FrozenMap(kwargs)  # pylint: disable=W0201
            return frkw

    @_AdderClass.decorate(classmethod)
    def get_constructor(cls):  # pylint: disable=E0213
        if hasattr(cls, 'constructor'):
            return cls.constructor  # pylint: disable=E1101
        if hasattr(cls, 'classpath'):
            return cls.classpath  # pylint: disable=E1101
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
