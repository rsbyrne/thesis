from everest.funcy.map import Map

from ..base import Datalike

class Structure(Datalike, Map):
    def __init__(self, *args, ignoreKeys = None, **kwargs):
        ignoreKeys = [] if ignoreKeys is None else ignoreKeys
        super().__init__(*args, **kwargs)
        self.dataKeys = tuple(k for k in self.keys() if not k in ignoreKeys)
    @property
    def data(self):
        return tuple(self[k] for k in self.dataKeys)
