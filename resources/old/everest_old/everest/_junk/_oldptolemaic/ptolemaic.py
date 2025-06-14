###############################################################################
''''''
###############################################################################
from functools import lru_cache

from everest.wordhash import w_hash
from everest import reseed

class Ptolemaic:
    # __slots__ = ('_callArgs', '_repr', '_hashID', 'instanceID')
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._callArgs = cls._process_callArgs(*args)
        obj.instanceID = str(reseed.digits(12))
        argstr = ', '.join(repr(a) for a in obj._callArgs)
        return obj
    @staticmethod
    def hash_or_repr(o):
        try:
            return o.hashID
        except AttributeError:
            return repr(o)
    @classmethod
    def _process_callArgs(cls, *args):
        return args
    def __repr__(self):
        try:
            return self._repr
        except AttributeError:
            argstr = ', '.join(self.hash_or_repr(a) for a in self._callArgs)
            self._repr = f'{type(self).__name__}({argstr})'
            return self._repr
    def __hash__(self):
        return int(self.instanceID)
    @property
    def hashID(self):
        try:
            return self._hashID
        except AttributeError:
            self._hashID = w_hash(repr(self))
            return self._hashID

###############################################################################
''''''
###############################################################################
