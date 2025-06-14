###############################################################################
''''''
###############################################################################

from abc import abstractmethod as _abstractmethod

from . import _classtools

from . import Ur as _Ur


@_classtools.MROClassable
class Dat(_Ur):

    mroclasses = ('Value',)

    @_abstractmethod
    def get_value(self):
        raise TypeError('Abstact methods should not be called.')

    class Value:
        def __get__(self, instance, owner = None):
            return instance.get_value()
        def __set__(self, instance, value):
            raise AttributeError("Can't set attribute.")
        def __delete__(self, instance):
            raise AttributeError("Can't set attribute.")

    def __init_subclass__(cls, /, *args, **kwargs):
        cls.value = cls.Value()
        super().__init_subclass__(*args, **kwargs)

Dat.UrBase = Dat


###############################################################################
###############################################################################
