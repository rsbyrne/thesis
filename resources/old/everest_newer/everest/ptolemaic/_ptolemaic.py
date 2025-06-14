###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod

from . import _classtools


class PtolemaicMeta(_ABCMeta):
    def __call__(cls, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)


@_classtools.Diskable
class Ptolemaic(metaclass = PtolemaicMeta):  # pylint: disable=R0903

    @classmethod
    @_abstractmethod
    def instantiate(cls, *args, **kwargs):
        '''Instantiates the class.'''
        raise TypeError(
            f"Class {cls} has no provided 'instantiate' method."
            )

    __slots__ = ('__dict__', '__weakref__')


###############################################################################
###############################################################################
