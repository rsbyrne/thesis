import inspect
import pickle

class Pyklet:
    _TAG_ = '_pyklet_'
    def __init__(self, *args, **kwargs):
        self._source = inspect.getsource(self.__class__)
        self._hashObjects = (args, kwargs, self._source)
        self._pickleClass = pickle.dumps(self.__class__)
        self._args, self._kwargs = args, kwargs
    def __reduce__(self):
        return (self._unpickle, (self._args, self._kwargs))
    @classmethod
    def _unpickle(cls, args, kwargs):
        return cls(*args, **kwargs)
