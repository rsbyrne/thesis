###############################################################################
''''''
###############################################################################

from ..exceptions import *

class Exception(Exception):
    pass

class MissingAsset(Exception, TypeError):
    pass

class ValueError(Exception, ValueError):
    pass
class NullValueDetected(ValueError):
    pass
class InfiniteValueDetected(ValueError):
    pass
class UnknownValueDetected(ValueError):
    pass

class EvaluationError(Exception):
    pass

class NotYetImplemented(Exception):
    pass

class RedundantConvert(Exception):
    pass

class CannotProcess(Exception):
    pass

class CannotDetermineDataType(Exception):
    pass

class ClosureExceptions(Exception):
    pass
class NothingToClose(ClosureExceptions):
    pass

class ConstructFailure(Exception):
    pass

###############################################################################
''''''
###############################################################################
