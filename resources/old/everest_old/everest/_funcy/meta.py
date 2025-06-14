###############################################################################
'''Defines the metaclass of all funcy objects.'''
###############################################################################

from abc import ABCMeta as _ABCMeta

from . import _wordhash, _reseed

class Meta(_ABCMeta):
    def __call__(cls, *args, **kwargs):
        inst = cls.__new__(cls, *args, **kwargs)
        args, kwargs = inst.args, inst.kwargs
        pickletup = inst._pickletup = (cls, args, kwargs)
        hashID = inst.hashID = _wordhash.w_hash(pickletup)
        hashint = inst.hashint = int(_reseed.rdigits(12, seed = hashID))
        inst.__init__(*args, **kwargs)
        return inst
