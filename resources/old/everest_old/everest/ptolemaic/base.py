###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC

from .schema import Schema as _Schema
from .case import Case as _Case

class Base(_ABC, metaclass = _Schema):
    hashID = None
    @classmethod
    def case_base(cls):
        return _Case
    def __repr__(self):
        return f'EverestInstance({self.hashID})'

###############################################################################
###############################################################################
