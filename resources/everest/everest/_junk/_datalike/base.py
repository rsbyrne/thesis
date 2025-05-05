###############################################################################
''''''
###############################################################################

from everest.funcy import Function

from .exceptions import *

class Datalike(Function):
    def __init__(self, *args, name = None, **kwargs):
        if name is None:
            raise ValueError("Datalikes must be provided a 'name' kwarg")
        super().__init__(*args, name = name, **kwargs)
    @property
    def semantics(self):
        return None
    @property
    def data(self):
        return self.value

###############################################################################
''''''
###############################################################################
