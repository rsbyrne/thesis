###############################################################################
''''''
###############################################################################
from . import Frame
from ..weaklist import WeakList

class Applier(Frame):
    def __init__(self,
            **kwargs
            ):
        self._pre_apply_fns = WeakList()
        self._apply_fns = WeakList()
        self._post_apply_fns = WeakList()
        super().__init__(**kwargs)
    def __call__(self, arg):
        self.apply(self, arg)
    def apply(self, arg):
        for fn in self._pre_apply_fns: fn()
        for fn in self._apply_fns: fn(arg)
        for fn in self._post_apply_fns: fn()

###############################################################################
''''''
###############################################################################
