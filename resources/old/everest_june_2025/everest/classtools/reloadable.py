###############################################################################
''''''
###############################################################################

from .adderclass import AdderClass as _AdderClass

def _unreduce(redcls, args, kwargs):
    return redcls(*args, **dict(kwargs))

class Reloadable(_AdderClass):
    def register_argskwargs(self, *args, **kwargs):
        try:
            _args = self._args
        except AttributeError:
            _args = self._args = list() # pylint: disable=W0201
        try:
            _kwargs = self._kwargs
        except AttributeError:
            _kwargs = self._kwargs = dict() # pylint: disable=W0201
        _args.extend(args)
        _kwargs.update(kwargs)
    @_AdderClass.decorate(property)
    def args(self):
        return tuple(self._args)
    @_AdderClass.decorate(property)
    def kwargs(self):
        return tuple(self._kwargs.items())
    @_AdderClass.decorate(classmethod)
    def get_constructor(cls): # pylint: disable=E0213
        if hasattr(cls, 'constructor'):
            return cls.constructor # pylint: disable=E1101
        # if hasattr(cls, 'classproxy'):
        if 'classproxy' in cls.__dict__:
            return cls.classproxy # pylint: disable=E1101
        return cls
    @_AdderClass.decorate(property)
    def unreduce(self): # pylint: disable=R0201
        return _unreduce
    @_AdderClass.forcemethod
    def __reduce__(self):
        return self.unreduce, self.get_redtup()
    def get_redtup(self):
        return self.get_constructor(), self.args, self.kwargs
    def copy(self):
        unredfn, args = self.__reduce__()
        return unredfn(*args) # pylint: disable=E1121

@Reloadable
class ClassProxy: # pylint: disable=R0903
    __slots__ = ('outercls', 'innercls', '_args', '_kwargs')
    def __init__(self, outercls, arg):
        self.outercls = outercls
        if isinstance(arg, str):
            self.innercls = getattr(outercls, arg)
        else:
            self.innercls = arg
            arg = arg.__name__
        self.register_argskwargs(outercls, arg) # pylint: disable=E1101
    def __call__(self, *args, **kwargs):
        return self.innercls(*args, **kwargs)

###############################################################################
###############################################################################
