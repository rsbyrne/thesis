from .derived import Derived
from .exceptions import *

class Trier(Derived):
    __slots__ = (
        'tryFunc',
        'altVal',
        'exception',
        )
    def __init__(self, tryFunc, altVal, exception = Exception):
        if not isinstance(tryFunc, Function):
            raise TypeError
        if not type(exception) is tuple:
            excTuple = (exception,)
        for e in excTuple:
            if not (isinstance(e, Exception) or issubclass(e, Exception)):
                raise TypeError
        self.tryFunc, self.exc, self.altVal = tryFunc, exception, altVal
        super().__init__(tryFunc, exception = exception, altVal = altVal)
    def evaluate(self):
        try:
            return self.tryFunc.value
        except self.exception:
            return self.altVal
