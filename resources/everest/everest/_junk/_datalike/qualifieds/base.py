###############################################################################
''''''
###############################################################################
from ..base import Datalike

class Qualified(Datalike):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for v in self.qualVars:
            if not isinstance(v, Datalike):
                raise TypeError("Provided qualVars must inherit from Datalike.")
    @property
    def qualVars(self):
        _, vars = self._qualVars()
        return tuple(vars)
    def _qualVars(self):
        yield None
    @property
    def qualKeys(self):
        for v in self.qualVars:
            yield v.name

###############################################################################
''''''
###############################################################################
