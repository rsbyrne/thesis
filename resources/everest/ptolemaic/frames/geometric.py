from collections.abc import Sequence, Collection, Iterable
from collections.abc import Iterator as abcIterator
from collections import OrderedDict, deque
from functools import partial, lru_cache, cached_property
import numbers

from everest.funcy import Fn
from everest.datalike.base import Datalike

from ..fundamentals import Case
from .producer import Producer
from .stateful import Stateful
from .indexable import Indexable
from .bythic import Bythic
from .exceptions import *
from ..ptolemaic import Ptolemaic
from ..display import message

class Geometric(Indexable, Stateful, Bythic):

    class GeometricException(PtolemaicException):
        pass
    class IterableNotReady(GeometricException):
        pass
    class PrematureStop(GeometricException):
        pass
    class MetricNotUnderstood(GeometricException, TypeError):
        pass
    class SetArgsNotUnderstood(GeometricException, TypeError):
        pass

    @classmethod
    def _iterator_construct(cls):
        class Iterator(abcIterator):
            __slots__ = ('frame', 'start', 'stop', 'step', 'stopped')
            def __init__(self,
                    frame,
                    start = None, stop = None, step = None, /
                    ):
                self.frame = frame
                if not start is None:
                    self.frame[...] = start
                self.stop, self.step = \
                    self._get_stop_fn(stop), self._get_step_fn(step)
                self.stopped = False
                super().__init__()
            def _get_stop_fn(self, stop, /):
                if type(stop) is tuple:
                    return Fn.all(Fn[tuple(
                        self._get_stop_fn(s) for s in stop
                        )])
                elif type(stop) is bool:
                    return stop
                elif stop is None:
                    return False
                else:
                    try:
                        index = self.frame.indices.get_index(stop)
                        return index >= stop
                    except NotIndexlike:
                        try:
                            return stop.allclose(self.frame)
                        except AttributeError:
                            raise self.frame.MetricNotUnderstood
            def _get_step_fn(self, step, /):
                if type(step) is tuple:
                    return Fn.any(Fn[tuple(
                        self._get_step_fn(s) for s in step
                        )])
                elif type(step) is bool:
                    return step
                elif step is None:
                    return True
                else:
                    try:
                        index = self.frame.indices.get_index(step)
                        return ~(index % step)
                    except NotIndexlike:
                        try:
                            return step.allclose(self.frame)
                        except AttributeError:
                            raise self.frame.MetricNotUnderstood
            def __next__(self):
                if self.stopped:
                    raise StopIteration
                while True:
                    try:
                        next(self.frame)
                    except self.frame.IterableNotReady:
                        self.frame.initialise()
                    except StopIteration:
                        raise PrematureStop
                    if self.stop:
                        self.stopped = True
                        break
                    if self.step:
                        break
                return self.frame.index.value
        cls.Case.Iterator = Iterator
        return

    @classmethod
    def _geometryClass_construct(cls):
        class Geometry(Datalike, Ptolemaic):
            # __slots__ = ('case', '_frame')
            def __init__(self, case, frame = None):
                self.case = case
                self._frame = frame
                super().__init__()
            @cached_property
            def frame(self):
                if self._frame is None:
                    return self.case()
                else:
                    return self._frame
        cls.Case.Geometry = Geometry
        return

    @classmethod
    def _geometry_construct(cls):
        class Stage(cls.Assembly, cls.Case.Geometry):
            ...
            # __slots__ = ('start')
            # def __init__(self, case, start, frame = None):
            #     self.start = start
            #     super().__init__(case, frame)
            # @property
            # def vars(self):
            #     frame = self.frame
            #     frame[...] = self.start
            #     return frame.state.vars
            # def _data(self):
            #     return self.value
            # def __getitem__(self, key):
            #     return self.case.StageVar(self, key)
            # def __len__(self):
            #     return len(self.frame.state)
            # def __iter__(self):
            #     return iter(self.frame.state)
        class StageVar(cls.Datum, cls.Case.Geometry):
            ...
            # __slots__ = ('stage', 'channel')
            # def __init__(self, stage, channel):
            #     self.stage, self.channel = stage, channel
            #     super().__init__(
            #         self.stage.case,
            #         frame = self.stage._frame
            #         )
            # @property
            # def var(self):
            #     return self.stage.vars[self.channel]
            # @property
            # def value(self):
            #     return self.var.value
        class Interval(cls.Magazine, cls.Case.Geometry):
            ...
            # __slots__ = ('case', 'start', 'stop', 'step')
            # def __init__(self,
            #         case,
            #         start, stop = None, step = True, /,
            #         frame = None,
            #         ):
            #     self.case = case
            #     self.start = start
            #     self.stop, self.step = stop, step
            #     super().__init__(case, frame)
            # def compute(self):
            #     frame = self.frame
            #     iterator = self.case.Iterator(
            #         frame,
            #         self.start, self.stop, self.step
            #         )
            #     for i in iterator:
            #         frame.store()
            #         yield i
            # def _data(self):
            #     self.frame.storage.tidy()
            #     inds = list(self.compute())
            #     return self.frame.storage.retrieve_val_dict(inds)
            # def __getitem__(self, index):
            #     return self.data[index]
            # def __len__(self):
            #     return len(self.data)
        class Bundle(cls.Ensemble, cls.Case.Geometry):
            ...
            # __slots__ = ('limPairs', 'starts', 'stops', 'step', 'Interval')
            # def __init__(self,
            #         case,
            #         starts, stops = None, step = None, /,
            #         frame = None,
            #         ):
            #     self.starts, self.stops = starts, stops
            #     self.Interval = partial(case.Interval, case, step = step)
            #     self.limPairs = Fn.seq.muddle(Fn[starts, stops])
            #     self.step = step
            #     super().__init__(case, frame)
            # def __contains__(self, arg):
            #     return arg in self.limPairs
            # def __iter__(self):
            #     for start, stop in self.limPairs:
            #         yield self.Interval(start, stop)
            # def __len__(self, arg):
            #     return len(self.limPairs)
            # def _data(self):
            #     return dict(zip(self.limPairs, (iv.data for iv in self)))
        cls.Case.Stage = Stage
        cls.Case.StageVar = StageVar
        cls.Case.Interval = Interval
        cls.Case.Bundle = Bundle
        return

    @classmethod
    def _case_construct(cls):
        super()._case_construct()
        class Case(cls.Case):
            def __getitem__(case, args):
                if not type(args) is tuple:
                    args = args,
                if len(args) > 1:
                    raise NotYetImplemented
                arg = args[0]
                if type(arg) is slice:
                    start, stop, step = arg.start, arg.stop, arg.step
                    # if any((isinstance(s, Iterable) for s in (start, stop))):
                    #     return case.bundle(start, stop, step)
                    # else:
                    return case.interval(start, stop, step)
                else:
                    return case.stage(arg)
            def stage(case, start, /, frame = None):
                return case.Stage(case, start)
            def interval(case, start, stop, step, /, frame = None):
                return case.Interval(case, start, stop, step, frame)
            def bundle(case, start, stop, step, /, frame = None):
                return case.Bundle(case, start, stop, step, frame)
        cls.Case = Case
        cls._iterator_construct()
        cls._geometryClass_construct()
        cls._geometry_construct()
        return

    def __init__(self,
            **kwargs,
            ):
        super().__init__(**kwargs)
        self.terminus = None
        self.iterator = partial(self.case.Iterator, self)
        for var in self.state.values():
            var.index = self.index

    def initialise(self):
        self.indices.zero()
        self._initialise()
    def _initialise(self):
        pass
    def __next__(self):
        try:
            self.index.value += 1
        except (TypeError, NullValueDetected):
            raise self.IterableNotReady
        try:
            self._iterate()
        except StopIteration:
            terminus = (i.value for i in self.indices.values())
            if len(terminus) > 1:
                self.terminus = terminus
            else:
                self.terminus = terminus[0]
            raise StopIteration
    def iterate(self):
        try:
            next(self)
        except self.IterableNotReady:
            self.initialise()
            next(self)
    def _iterate(self):
        pass

    def _setitem(self, keyvals, /):
        super()._setitem(keyvals)
        key, val = keyvals.popleft()
        try:
            if type(key) is str:
                if key != 'metric':
                    raise self.SetArgsNotUnderstood
            elif not key is Ellipsis:
                raise self.SetArgsNotUnderstood
            try:
                iterator = self.iterator(None, val, False)
            except self.MetricNotUnderstood:
                raise self.SetArgsNotUnderstood
            endpoint, = iterator
        except self.SetArgsNotUnderstood:
            keyvals.appendleft((key, val))

    def _report(self):
        yield repr(self)
        try:
            yield from self.indices._report()
            yield from self.state._report()
        except NullValueDetected:
            yield "null"
    def report(self):
        out = ''
        out += repr(self)
        indent = ' ' * 4
        nl = '\n'
        for sub in (self.indices, self.state):
            header, *content = sub._report()
            out += f'{nl}{indent}{header}{nl}{indent * 2}'
            out += f'{nl}{indent * 2}'.join(content)
        message(out)
