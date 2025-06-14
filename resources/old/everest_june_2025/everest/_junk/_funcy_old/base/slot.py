###############################################################################
''''''
###############################################################################

from . import _special
from .base import Base as _Base

from .exceptions import *

class Slot(_Base):

    open = True

    __slots__ = (
        'slots',
        'argslots',
        'kwargslots',
        )

    def __init__(self, *, name = None):
        self.slots = 1
        if name is None:
            self.argslots = 1
            self.kwargslots = []
        else:
            self.argslots = 0
            self.kwargslots = [name]
        super().__init__(name = name)
        # raise Exception("Cannot close a Slot function.")
    def __call__(self, arg):
        return arg
    def evaluate(self):
        try:
            return self.tempVal
        except AttributeError:
            return _special.null
    @property
    def value(self):
        return self.evaluate()
    def register_downstream(self, registrant):
        pass
    def refresh(self):
        pass

###############################################################################
''''''
###############################################################################
