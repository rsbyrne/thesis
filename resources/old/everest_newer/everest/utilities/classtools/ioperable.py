###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod

from .adderclass import AdderClass as _AdderClass
from .operable import Operable as _Operable


class IOperable(_AdderClass):

    get_operator = _Operable.get_operator

    @_AdderClass.decorate(_abstractmethod)
    def ioperate(self, operator, arg0, /) -> object:  # pylint: disable=R0201
        '''Carries out the actual operation in place and returns self.'''
        raise TypeError(
            "This method is abstract and should never be called."
            )

    def _iop(self, other=None, /, *, operator):
        operator = self.get_operator(operator)
        return self.ioperate(operator, other)

    # INPLACE

    def __iadd__(self, other):
        return self._iop(other, operator='add')

    def __isub__(self, other):
        return self._iop(other, operator='sub')

    def __imul__(self, other):
        return self._iop(other, operator='mul')

    def __imatmul__(self, other):
        return self._iop(other, operator='matmul')

    def __itruediv__(self, other):
        return self._iop(other, operator='truediv')

    def __ifloordiv__(self, other):
        return self._iop(other, operator='floordiv')

    def __imod__(self, other):
        return self._iop(other, operator='mod')

    def __idivmod__(self, other):
        return self._iop(other, operator='divmod')

    def __ipow__(self, other):
        return self._iop(other, operator='pow')

    # def __lshift__(self, other):
    #     return self._iop(other, operator='lshift')

    # def __rshift__(self, other):
    #     return self._iop(other, operator='rshift')

    def __iand__(self, other):
        return self._iop(other, operator='and')

    def __ixor__(self, other):
        return self._iop(other, operator='or')

    def __ior__(self, other):
        return self._iop(other, operator='xor')


###############################################################################
###############################################################################
