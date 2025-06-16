from functools import wraps
import weakref

from everest.grouper import Grouper
from everest.ptolemaic.frames import Producer

from ..weaklist import WeakList

from ..exceptions import *
class ObservableError(EverestException):
    pass
class ObservableMissingAsset(MissingAsset, ObservableError):
    pass
class NoObserver(EverestException):
    pass
class ObservationModeError(EverestException):
    pass

# def _observation_mode(func):
#     @wraps(func)
#     def wrapper(self, *args, **kwargs):
#         try:
#             self._observation_mode_hook()
#             print("here")
#             divertFunc = getattr(self, '_observer_' + func.__name__.strip('_'))
#             return divertFunc(*args, **kwargs)
#         except NoObserver:
#             return func(self, *args, **kwargs)
#     return wrapper

class Obs:
    def __init__(self, host):
        self._host = weakref.ref(host)
    @property
    def host(self):
        host = self._host()
        assert not host is None
        return host
    def __getattr__(self, key):
        try:
            return self._get_out(key)
        except KeyError:
            raise AttributeError
    def _get_out(self, key):
        chosen = None
        for observer in self.host.observers:
            if key in observer.keys():
                chosen = observer
                break
        if chosen is None:
            for observerClass in self.host._observerClasses:
                observer = observerClass()
                if key in observer.keys():
                    chosen = observer
                    break
        if chosen is None:
            raise KeyError
        with chosen(self.host):
            return self.host.storage[key]

class Observable(Producer):

    def __init__(self,
            **kwargs
            ):

        self._observer = None
        self.observers = WeakList()
        self._observerClasses = WeakList()
        # self.observers = list()
        # self._observerClasses = list()
        if 'observers' in dir(self.ghosts):
            for o in self.ghosts.observers:
                if isinstance(o, Observer):
                    self.observers.append(o)
                elif type(o) is type(Observer):
                    self._observerClasses.append(o)
                else:
                    raise TypeError
        self.obs = Obs(self)

        super().__init__(**kwargs)

    def _observation_mode_hook(self):
        pass

    # def _outputSubKey(self):
    #     for o in super()._outputSubKey():
    #         yield o
    #     try:
    #         yield self.observer.hashID
    #     except NoObserver:
    #         yield ''

    @property
    def _observationMode(self):
        return not self._observer is None

    @property
    def observer(self):
        if not self._observationMode:
            raise NoObserver
        return self._observer

    def _out(self):
        outs = super()._out()
        if self._observationMode:
            add = self.observer._out()
        else:
            add = {}
        outs.update(add)
        return outs
    def _load(self, *args, **kwargs):
        if not self._observer is None:
            raise ObservationModeError(
                "Cannot load state while in Observer Mode."
                )
        super()._load(*args, **kwargs)

    # def _store(self, *args, **kwargs):
    #     super()._store(*args, **kwargs)
    #     if self._observer is None:
    #         for observer in self.observers:
    #             with observer(self):
    #                 super().store(*args, **kwargs)
    # def _save(self, *args, **kwargs):
    #     super()._save(*args, **kwargs)
    #     if self._observer is None:
    #         for observer in self.observers:
    #             with observer(self):
    #                 super().save(*args, **kwargs)
    #                 self.writeouts.add(observer, 'observer')
    # def _clear(self, *args, **kwargs):
    #     super()._clear(*args, **kwargs)
    #     if self._observer is None:
    #         for observer in self.observers:
    #             with observer(self):
    #                 self._clear(*args, **kwargs)

# At bottom to avoid circular reference
from ._observer import Observer
