###############################################################################
''''''
###############################################################################


import weakref as _weakref

from .shade import Shade as _Shade


class Singleton(_Shade):

    @classmethod
    def _cls_extra_init_(cls, /):
        cls.premade = _weakref.WeakValueDictionary()
        try:
            nextmeth = super()._cls_extra_init_
        except AttributeError:
            pass
        else:
            nextmeth()

    @classmethod
    def prekey(cls, params):
        return params.__str__()

    @classmethod
    def instantiate(cls, params):
        premade = cls.premade
        prekey = cls.prekey(params)
        if prekey in premade:
            return premade[prekey]
        obj = type(cls).instantiate(cls, params)
        premade[prekey] = obj
        return obj


###############################################################################
###############################################################################
