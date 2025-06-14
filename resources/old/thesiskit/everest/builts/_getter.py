from . import Built
from ..weaklist import WeakList

class Getter(Built):
    def __init__(self,
            **kwargs
            ):
        self._get_fns = WeakList()
        super().__init__(**kwargs)
    def __getitem__(self, indexer):
        if type(indexer) is tuple:
            return (self._getter_get(o) for o in indexer)
        else:
            return self._getter_get(indexer)
    def _getter_get(self, indexer):
        for fn in self._get_fns:
            out = fn(indexer)
            if not out is None:
                break
        return out
