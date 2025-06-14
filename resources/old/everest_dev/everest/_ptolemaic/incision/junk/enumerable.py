###############################################################################
''''''
###############################################################################


from .orderable import Orderable as _Orderable


class Advanceable(_Orderable):

#     @classmethod
#     def add_defer_methods(cls, ACls, /):
#         def __iter__(self):
#             return map(self.retrieve, self.chora.__iter__())
#         ACls.__iter__ = __iter__
#         super().add_defer_methods(ACls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._iterfn = {
            (False, True): self._iter_ubnd,
            (True, False): self._iter_lbnd,
            (True, True): self._iter_dbnd,
            }[tuple(bnd is not None for bnd in self.bnds)]

    def _iter_lbnd(self):
        val, advancer = self.lbnd, self.advancer
        while True:
            yield val
            val = advancer(val)

    def _iter_ubnd(self):
        advancer = self.advancer
        val = yield
        while True:
            if comparator(val, ubnd) > -1:
                return
            yield val
            val = advancer(val)

    def _iter_dbnd(self):
        comparator, ubnd = self.comparator, self.ubnd
        for val in self._iter_lbnd():
            if comparator(val, ubnd) > -1:
                return
            yield val

#     def (self):
#         return self._iterfn()


###############################################################################
###############################################################################
