from collections import OrderedDict

from everest.frames._observer import Observer, ObserverConstruct

from ..exceptions import *

class CrisisObserver(Observer):

    def __init__(self,
            obskeys,
            **kwargs
            ):
        self._keys = lambda: obskeys
        super().__init__(**kwargs)

    def _construct(self, subject):
        analysers = self._user_construct(subject)
        analysers = dict(zip(self.keys(), analysers))
        return ObserverConstruct(self, subject, **analysers)

    def _user_construct(self, observables, inputs):
        raise MissingAsset("User must provide _user_construct method.")
