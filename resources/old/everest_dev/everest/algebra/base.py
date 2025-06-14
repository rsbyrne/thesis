###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod

from . import _utilities


class AlgebraBase:

    ...


class AlgebraMeta(AlgebraBase, _ABCMeta):

    def _cls_repr(cls):
        return ''

    @_utilities.caching.softcache(None)
    def _cls_repr_(cls):
        clsname = cls._cls_repr()
        if not clsname:
            return cls.__name__
        return f"{type(cls).__name__}({clsname})"

    def __repr__(cls):
        return cls._cls_repr_()


class AlgebraInstance(AlgebraBase, metaclass=AlgebraMeta):

    def __eq__(self, other):
        return repr(self) == repr(other)

    @_abstractmethod
    def _repr(self):
        '''Should return an unambiguous representation of the object.'''
        raise NotImplementedError

    @_utilities.caching.softcache(None)
    def __repr__(self):
        return f"{repr(type(self))}({self._repr()})"

    @_utilities.caching.softcache(None)
    def __hash__(self):
        return hash(self._repr())


###############################################################################
###############################################################################
