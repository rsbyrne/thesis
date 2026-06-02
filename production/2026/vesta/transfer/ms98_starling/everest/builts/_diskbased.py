from . import Built
from . import GLOBALANCHOR
from ..exceptions import EverestException

class DiskBasedFail(EverestException):
    pass

class DiskBased(Built):

    def __init__(self, *args, **kwargs):
        if (self.name is None) or (self.path is None):
            raise DiskBasedFail
        super().__init__(*args, **kwargs)
