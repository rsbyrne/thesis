from collections.abc import Iterator
from collections import deque

from .base import Frame
from .exceptions import *

class LeftoverException(PtolemaicException, ValueError):
    pass

class ForeverIterable(Iterator):
    def __init__(self, val):
        self.val = val
    def __iter__(self):
        return self
    def __next__(self):
        return self.val

class Bythic(Frame):

    def __setitem__(self, keys, vals):
        if keys is Ellipsis:
            keys = ForeverIterable(Ellipsis)
            keyvals = deque(zip(keys, vals))
        elif type(keys) is slice:
            if all(a is None for a in (slice.start, slice.stop, slice.step)):
                keyvals = ForeverIterable((Ellipsis, vals))
            else:
                raise NotYetImplemented
        else:
            keyvals = deque(zip(keys, vals))
        try:
            self._setitem(keyvals)
            if keyvals:
                raise LeftoverException
        except IndexError:
            pass
        self._bythic_changed_state_hook()

    def _setitem(self, keyvals, /):
        pass

    def _bythic_changed_state_hook(self):
        pass
