###############################################################################
''''''
###############################################################################


import weakref as _weakref

from .diskable import Diskable as _Diskable


class ParameterisableMeta(type):

    unique = False

    def __init__(cls, /, *args, **kwargs):
        _ = _Diskable(cls)
        if not hasattr(cls, 'parameterise'):
            raise TypeError("Class must provide 'parameterise' method.")
        if cls.unique:
            cls.premade = _weakref.WeakValueDictionary()
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        args, kwargs = cls.parameterise(*args, **kwargs)
        obj = cls.__new__(cls, *args, **kwargs)
        obj.register_argskwargs(*args, **kwargs)
        if cls.unique:
            if (hashID := obj.hashID) in (dct := cls.premade):
                return dct[hashID]
            dct[hashID] = obj
        obj.__init__(*args, **kwargs)
        return obj


class Parameterisable:

    def parameterise(self, /):
        pass


###############################################################################
''''''
###############################################################################