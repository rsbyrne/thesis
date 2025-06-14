from ..exceptions import *

class PtolemaicException(Exception):
    pass

class NotYetImplemented(PtolemaicException):
    pass

class MissingAsset(PtolemaicException):
    pass

from everest.funcy.exceptions import NullValueDetected
