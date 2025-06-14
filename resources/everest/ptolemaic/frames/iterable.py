from functools import wraps, cached_property
import numbers
import warnings
from collections import OrderedDict
from collections.abc import Iterable as abcIterable
from collections.abc import Iterator as abcIterator
from collections.abc import Sequence
import weakref

from everest.funcy import Fn, NullValueDetected
from everest import wordhash

from ..fundamentals.case import Case
from .producer import LoadFail
from .indexable import NotIndexlike
from .geometric import Geometric
from .bythic import Bythic

from .exceptions import *
class IterableException(EverestException):
    pass
class IterableMissingAsset(MissingAsset, IterableException):
    pass
class IterableAlreadyInitialised(IterableException):
    pass
class IterableNotInitialised(IterableException):
    pass
class RedundantIterate(IterableException):
    pass
class IterableEnded(StopIteration, IterableException):
    pass
class BadStrategy(IterableException):
    pass
class ExhaustedStrategies(IterableException):
    pass

def _iterable_initialise_if_necessary(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except NullValueDetected:
            self.initialise()
            return func(self, *args, **kwargs)
    return wrapper

class Iterable(Geometric):

    def __init__(self,
            **kwargs
            ):
        super().__init__(**kwargs)

    @property
    def initialised(self):
        return self.indices.iszero
    @property
    def postinitialised(self):
        return self.indices.ispos
    @_iterable_initialise_if_necessary
    def get_storage(self, *args, **kwargs):
        return super().get_storage(*args, **kwargs)

    def _try_load(self, stop, /):
        try: self.load(stop)
        except LoadFail: raise BadStrategy
    def _try_convert(self, stop, /):
        try: return Fn(stop)
        except (ValueError, TypeError): raise BadStrategy
    def _try_index(self, stop, /):
        try: return self.indices.get_index(stop)
        except NotIndexlike: raise BadStrategy
    def _try_strats(self, strats, *args, **kwargs):
        for strat in strats:
            try: return strat(*args, **kwargs)
            except BadStrategy: pass
        raise ExhaustedStrategies("Could not find a strategy to proceed.")

    # REACH
    def reach(self, arg, /, *args, **kwargs):
        self._reach(arg, **kwargs)
        if args:
            self.stride(*args, **kwargs)
    def _reach(self, stop = None, /, **kwargs):
        if stop is None:
            self._reach_end()
        else:
            strats = (
                self._try_load,
                self._reach_index,
                self._reach_fn
                )
            self._try_strats(strats, stop, **kwargs)
    def _reach_end(self, /, **kwargs):
        presentCount = self.index.value
        if presentCount == self.terminus: return None
        stored = self.storage[self.index.name]
        if stored:
            i = max(stored)
            if i != presentCount:
                self.load(i)
            if i == self.terminus: return None
        self.go(None, **kwargs)
    @_iterable_initialise_if_necessary
    def _reach_index(self, stop, /, index = None):
        if index is None:
            index = self._try_index(stop)
        if index == stop:
            raise StopIteration
        self.storage.tidy()
        stored = self.storage[index.name]
        try:
            stored = stored[stored <= stop].max()
            self.load_index(stored)
            if stored == stop:
                return
        except (IndexError, ValueError):
            if index.value > stop:
                self.reset()
        stop = index >= stop
        while not stop:
            self.iterate()
    def _reach_fn(self, stop, /, **kwargs):
        stop = self._try_convert(stop)
        try:
            self.load(stop)
        except LoadFail:
            self.reset()
            closed = stop.allclose(self)
            while not closed:
                self.iterate(**kwargs)

    # STRIDE
    def stride(self, /, *args, **kwargs):
        for arg in args:
            self._stride(arg, **kwargs)
    def _stride(self, stop, /, **kwargs):
        try:
            index = self._try_index(stop)
            stop = (index + stop).value
            return self._reach_index(stop, index, **kwargs)
        except BadStrategy:
            pass
        return self._go_fn(stop, **kwargs)

    # GO
    def go(self, arg, /, *args, **kwargs):
        self._go(arg)
        for arg in args:
            self._go(arg, **kwargs)
    def _go(self, stop = None, /, **kwargs):
        if stop is None:
            self._go_indefinite(**kwargs)
        elif issubclass(type(stop), numbers.Integral):
            self._go_integral(stop, **kwargs)
        else:
            strats = (self._go_index, self._go_fn)
            self._try_strats(*strats, stop = stop, **kwargs)
    def _go_indefinite(self, /):
        try:
            while True:
                self.iterate()
        except StopIteration:
            pass
        self.terminus = self.indices[0].value
    def _go_integral(self, stop, /, **kwargs):
        for _ in range(stop):
            self.iterate(**kwargs)
    def _go_index(self, stop, /, index = None, **kwargs):
        index = self._try_index(stop)
        stop = (index + stop).value
        while index < stop:
            self.iterate(**kwargs)
    def _go_fn(self, stop, /, **kwargs):
        stop = self._try_convert(stop)
        stop = stop.allclose(self)
        while not stop:
            self.iterate(**kwargs)

    # RUN
    def run(self, /, *args, **kwargs):
        self.reset()
        self.go(*args, **kwargs)

    def _load_out(self, arg):
        if type(arg) is type:
            if issubclass(arg, StopIteration):
                if self.terminus is None:
                    raise LoadFail
                return self.load_index(self.terminus)
        return super()._load_out(arg)
