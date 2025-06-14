from ..exceptions import *

class FuncyException(Exception):
    pass

class MissingAsset(FuncyException, TypeError):
    pass

class FuncyValueError(FuncyException, ValueError):
    pass
class NullValueDetected(FuncyValueError):
    pass
class InfiniteValueDetected(FuncyValueError):
    pass
class UnknownValueDetected(FuncyValueError):
    pass

class EvaluationError(FuncyException):
    pass

class NotYetImplemented(Exception):
    pass

class RedundantConvert(FuncyException):
    pass

class CannotProcess(FuncyException):
    pass

class CannotDetermineDataType(FuncyException):
    pass

class ClosureExceptions(FuncyException):
    pass
class NothingToClose(ClosureExceptions):
    pass
