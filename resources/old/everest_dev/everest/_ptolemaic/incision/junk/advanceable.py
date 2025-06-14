###############################################################################
''''''
###############################################################################


from .sett import Sett as _Sett
from .sliceable import Sliceable as _Sliceable
from .bounded import Bounded as _Bounded


class _Advanceable_(_Sett):

    def __init__(self, *args, advancer, **kwargs):
        self.advancer = advancer
        self.register_argskwargs(advancer=advancer)
        super().__init__(*args, **kwargs)

    @classmethod
    def add_defer_methods(cls, ACls, /):
        def __iter__(self):
            return map(self.retrieve, self.chora.__iter__())
        ACls.__iter__ = __iter__
        super().add_defer_methods(ACls)

    def __iter__(self):
        advancer = self.advancer
        val = yield
        while True:
            yield val
            val = advancer(val)


class Progression(_Bounded, _Advanceable_):

    def __init__(self, *args, last=False, **kwargs):
        self.last = last
        self.register_argskwargs(last=last)
        super().__init__(*args, **kwargs)
        self._iterfn = {
            (False, True): self._iter_ubnd,
            (True, False): self._iter_lbnd,
            (True, True): self._iter_dbnd,
            }[tuple(bnd is not None for bnd in self.bnds)]

    def _iter_lbnd(self):
        advancer, val = self.advancer, self.lbnd
        while True:
            yield val
            val = advancer(val)

    def _iter_ubnd(self):
        advancer, ubnd = self.advancer, self.ubnd
        val = yield
        while not ubnd(val):
            yield val
            val = advancer(val)
        if self.last:
            yield val

    def _iter_dbnd(self):
        advancer, val, ubnd = self.advancer, self.lbnd, self.ubnd
        while not ubnd(val):
            yield val
            val = advancer(val)
        if self.last:
            yield val

    def __iter__(self):
        return self._iterfn()


class Advanceable(_Advanceable_, _Sliceable):

    Progression = Progression

    @classmethod
    def slice_methods(cls, /):
        for comb in ((True, True), (True, False), (False, True)):
            yield (*comb, False), cls.incise_enbounding_slice
        yield from super().slice_methods()

    def incise_enbounding(self, start, stop, /):
        return Progression(
            *self.args,
            **(self.kwargs | dict(lbnd=start, ubnd=stop)),
            )


###############################################################################
###############################################################################
