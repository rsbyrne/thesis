###############################################################################
''''''
###############################################################################


from .adderclass import AdderClass as _AdderClass
from . import _makehash


# @_AdderClass.wrapmethod
# def extra_init(calledmeth, obj, *args, **kwargs):
#     obj._hashID, obj._hashint, obj._hashstr = None, None, None
#     calledmeth(obj, *args, **kwargs)
    # if 'get_hashID' in dir(obj):
    #     hashval = obj.get_hashID()  # pylint: disable=E1101
    # else:
    #     hashval = _makehash.word_hash(obj)
    # obj._hashID = hashval  # pylint: disable=W0212


class HashIDable(_AdderClass):
    ...

    # toadd = dict(
    #     __init__=extra_init,
    #     )

    reqslots = ('_hashID', '_hashint', '_hashstr', '_repr')

    @_AdderClass.decorate(property)
    def hashstr(self):
        try:
            return self._hashstr
        except AttributeError:
            hashval = self._hashstr = _makehash.quick_hash(self)  # pylint: disable=W0201
            return hashval

    @_AdderClass.decorate(property)
    def hashint(self):
        try:
            return self._hashint
        except AttributeError:
            hashval = self._hashint = int(self.hashstr, 16)  # pylint: disable=W0201
            return hashval

    @_AdderClass.decorate(property)
    def hashID(self):
        try:
            return self._hashID
        except AttributeError:
            if hasattr(self, 'get_hashID'):
                hashval = self.get_hashID()  # pylint: disable=E1101
            else:
                hashval = _makehash.word_hash(self)
            self._hashID = hashval  # pylint: disable=W0201
            return hashval

    @_AdderClass.forcemethod
    def __hash__(self):
        return self.hashint

    @_AdderClass.forcemethod
    def __repr__(self):
        try:
            return self._repr
        except AttributeError:
            _repr = self._repr = f"{type(self).__name__}({self.hashID})"
            return _repr


###############################################################################
###############################################################################
