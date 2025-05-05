###############################################################################
''''''
###############################################################################

from abc import abstractmethod as _abstractmethod

from .methadder import MethAdder as _MethAdder
# from .operable import Operable

class Evaluable(_MethAdder):

    @_MethAdder.decorate(property)
    def value(self):
        ...


    @_abstractmethod
    def set_value(self, val):
        '''Assigns the value to self.'''
        raise TypeError(
            "This method is abstract and should not ever be called."
            )

#
# operator.iadd(a, b)
# operator.__iadd__(a, b)
# a = iadd(a, b) is equivalent to a += b.
#
# operator.iand(a, b)
# operator.__iand__(a, b)
# a = iand(a, b) is equivalent to a &= b.
#
# operator.iconcat(a, b)
# operator.__iconcat__(a, b)
# a = iconcat(a, b) is equivalent to a += b for a and b sequences.
#
# operator.ifloordiv(a, b)
# operator.__ifloordiv__(a, b)
# a = ifloordiv(a, b) is equivalent to a //= b.
#
# operator.ilshift(a, b)
# operator.__ilshift__(a, b)
# a = ilshift(a, b) is equivalent to a <<= b.
#
# operator.imod(a, b)
# operator.__imod__(a, b)
# a = imod(a, b) is equivalent to a %= b.
#
# operator.imul(a, b)
# operator.__imul__(a, b)
# a = imul(a, b) is equivalent to a *= b.
#
# operator.imatmul(a, b)
# operator.__imatmul__(a, b)
# a = imatmul(a, b) is equivalent to a @= b.
#
# New in version 3.5.
#
# operator.ior(a, b)
# operator.__ior__(a, b)
# a = ior(a, b) is equivalent to a |= b.
#
# operator.ipow(a, b)
# operator.__ipow__(a, b)
# a = ipow(a, b) is equivalent to a **= b.
#
# operator.irshift(a, b)
# operator.__irshift__(a, b)
# a = irshift(a, b) is equivalent to a >>= b.
#
# operator.isub(a, b)
# operator.__isub__(a, b)
# a = isub(a, b) is equivalent to a -= b.
#
# operator.itruediv(a, b)
# operator.__itruediv__(a, b)
# a = itruediv(a, b) is equivalent to a /= b.
#
# operator.ixor(a, b)
# operator.__ixor__(a, b)
# a = ixor(a, b) is equivalent to a ^= b.
