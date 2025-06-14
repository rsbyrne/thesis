###############################################################################
''''''
###############################################################################
from collections.abc import Set

from ..slot import Slot

class Sett(Slot, Set):
    __slots__ = (
        'dtype',
        )
    def __init__(self, dtype, /, **kwargs):
        self.dtype = dtype
        try:
            name = self.dtype.__name__
        except AttributeError:
            name = str(self.dtype)
        super().__init__(name = name, **kwargs)
    def __contains__(self, val):
        if isinstance(val, self.dtype):
            return True
        else:
            pass
        try:
            return issubclass(val, self.dtype)
        except TypeError:
            pass
        try:
            _ = self.dtype(arg)
            return True
        except (TypeError, ValueError):
            pass
        return False
    def __iter__(self):
        raise StopIteration
    def __len__(self):
        return inf
    def _namestr(self):
        return self.name
    def _valstr(self):
        return ''
    def evaluate(self):
        raise ValueError("Meaningless to evaluate an abstract set.")
    def __call__(self, arg):
        return self.dtype(arg)

###############################################################################
''''''
###############################################################################
