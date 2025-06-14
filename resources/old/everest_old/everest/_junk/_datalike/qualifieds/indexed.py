###############################################################################
''''''
###############################################################################
from .base import Qualified
from ..datums.numerical.index import Index

class Indexed(Qualified):
    def __init__(self, *args, _indexVars, **kwargs):

        super().__init__(*args, **kwargs)
        for v in self.indexVars:
            if not isinstance(v, Index):
                raise TypeError("Provided indexVars must inherit from Index.")
    @property
    def indexVars(self):
        _, vars = self._indexVars()
        return tuple(vars)
    def _indexVars(self):
        yield None
    @property
    def indexKeys(self):
        for v in self.indexVars:
            yield v.name
    def _qualVars(self):
        yield from super()._qualVars()
        yield from self.indexVars

# class Counted(Indexed):
#     def __init__(self, *args, countVar, **kwargs):
#         self.countVar = countVar
#         super().__init__(*args, **kwargs)
#     def _indexVars(self):
#         yield from super()._indexVars()
#         yield self.countVar
#
# class Chroned(Indexed):
#     def __init__(self, *args, chronVar, **kwargs):
#         self.chronVar = chronVar
#         super().__init__(*args, **kwargs)
#     def _indexVars(self):
#         yield from super()._indexVars()
#         yield self.chronVar

###############################################################################
''''''
###############################################################################
