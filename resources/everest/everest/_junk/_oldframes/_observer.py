###############################################################################
''''''
###############################################################################
from functools import wraps
from contextlib import contextmanager
import weakref
from collections import OrderedDict
from collections.abc import Mapping

from ._observable import Observable
from ._promptable import Promptable
from ..freq import Freq

from ..exceptions import *
class ObserverError(EverestException):
    '''An error has emerged related to the Observer class.'''
class ObserverInputError(ObserverError):
    '''Observer subjects must be instances of Observable class.'''
class ObserverMissingAsset(ObserverError, MissingAsset):
    pass
class AlreadyAttachedError(ObserverError):
    '''Observer is already attached to that subject.'''
class NotAttachedError(ObserverError):
    '''Observer is not attached to a subject yet.'''

def _attached(func):
    @wraps(func)
    def wrapper(self, *args, silent = False, **kwargs):
        if self.subject is None and not silent:
            raise NotAttachedError
        return func(self, *args, **kwargs)
    return wrapper
def _unattached(func):
    @wraps(func)
    def wrapper(self, *args, silent = False, **kwargs):
        if not self.subject is None and not silent:
            raise AlreadyAttachedError
        return func(self, *args, **kwargs)
    return wrapper

class ObserverConstruct(Mapping):

    def __new__(cls, host, subject, *args, **kwargs):
        obj = super().__new__(cls)
        obj._host = host
        obj._subject = subject
        return obj
    def __init__(self, host = None, subject = None, **analysers):
        self.analysers = OrderedDict(sorted(analysers.items()))
        self.freq = Freq()
        super().__init__()

    @property
    def host(self):
        return self._host
    @property
    def subject(self):
        return self._subject

    def _out(self):
        return OrderedDict((k, v.value) for k, v in self.items())
    def out(self):
        with self.host(self.subject):
            return self.host.out()
    def store(self):
        with self.host(self.subject):
            self.host.store()
    def save(self):
        with self.host(self.subject):
            self.host.save()
    def clear(self):
        with self.host(self.subject):
            return self.host.clear()

    def prompt(self):
        self._prompt()
    def _prompt(self):
        if self.freq:
            self.store()

    def __getitem__(self, key):
        return self.analysers[key]
    def __len__(self):
        return len(self.analysers)
    def __iter__(self):
        for a in self.analysers.values():
            yield a.evaluate

    def keys(self):
        return self.analysers.keys()
    def items(self):
        return self.analysers.items()

    def __getattr__(self, name):
        try:
            return self.analysers[name].value
        except KeyError:
            raise AttributeError

class Observer(Promptable):

    def __init__(self,
            **kwargs
            ):

        self.subject = None
        self.constructs = weakref.WeakKeyDictionary()

        super().__init__(**kwargs)

    @_unattached
    def attach(self, subject):
        self.register(subject, silent = True)
        self.subject = subject
        self.subject._observer = self
    @_attached
    def detach(self, subject):
        self.subject._observer = None
        self.subject = None

    @contextmanager
    def observe(self, subject):
        if self.subject is None:
            self.attach(subject)
            try:
                yield self.get_construct(subject)
            finally:
                self.detach(subject)
        else:
            if subject is self.subject:
                try:
                    yield
                finally:
                    pass
            else:
                raise AlreadyAttachedError

    def __call__(self, subject):
        return self.observe(subject)

    def register(self, subject, silent = False):
        if not isinstance(subject, Observable):
            raise TypeError(
                "Observee must be an instance of the Observable class."
                )
        if not self in subject.observers:
            subject.observers.append(self)
        else:
            if not silent:
                raise ObserverError("Observer already registered.")
    def deregister(self, subject):
        if not isinstance(subject, Observable):
            raise TypeError(
                "Observee must be an instance of the Observable class."
                )
        if self in subject.observers:
            subject.observers.remove(self)
        else:
            if not silent:
                raise ObserverError("Observer not registered.")

    def construct(self, subject):
        construct = self._construct(subject)
        if not isinstance(construct, ObserverConstruct):
            raise ObserverError(
                "Observer construct must inherit ObserverConstruct class."
                )
        return construct

    def _construct(self, subject):
        raise MissingAsset("Observer must provide _construct method.")

    @property
    @_attached
    def active(self):
        return self.get_construct(self.subject)

    def _out(self):
        return self.active._out()
    @_attached
    def out(self):
        return self.subject.out()
    @_attached
    def store(self):
        self.subject.store()
    @_attached
    def save(self):
        self.subject.writeouts.add(self, 'observer')
        self.subject.save()
    @_attached
    def clear(self):
        self.subject.clear()

    def keys(self):
        return self._keys()
    def _keys(self):
        raise MissingAsset("Observer must provide _keys method.")

    def get_construct(self, subject):
        try:
            construct = self.constructs[subject]()
            if construct is None:
                raise KeyError
        except KeyError:
            construct = self.construct(subject)
            self.constructs[subject] = weakref.ref(construct)
        return construct
    def __getitem__(self, subject):
        return self.get_construct(subject)

    def prompt(self, prompter):
        with self(prompter):
            self.active.prompt()

    # def _prompt(self, prompter):
    #     # Overrides Promptable _prompt method:
    #     if self.subject is None:
    #         with self.attach(prompter):
    #             super()._prompt(prompter)
    #     elif prompter is self.subject:
    #         super()._prompt(prompter)
    #     else:
    #         raise AlreadyAttachedError

###############################################################################
''''''
###############################################################################
