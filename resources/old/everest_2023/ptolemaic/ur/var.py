###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod

from . import _classtools

from . import Ur as _Ur


@_classtools.MROClassable
class Var(_Ur):

    mroclasses = ('Value',)

    @_abstractmethod
    def get_value(self):
        raise TypeError('Abstact methods should not be called.')
    @_abstractmethod
    def set_value(self, value):
        raise TypeError('Abstact methods should not be called.')
    @_abstractmethod
    def del_value(self):
        raise TypeError('Abstact methods should not be called.')

    def __ilshift__(self, b):
        self.set_value(b)
        return self

    class Value:
        def __get__(self, instance, owner = None):
            return instance.get_value()
        def __set__(self, instance, value):
            instance.set_value(value)
        def __delete__(self, instance):
            instance.del_value()

    def __init_subclass__(cls, /, *args, **kwargs):
        cls.value = cls.Value()
        super().__init_subclass__(*args, **kwargs)

Var.UrBase = Var


###############################################################################
###############################################################################
