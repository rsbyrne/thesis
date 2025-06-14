###############################################################################
''''''
###############################################################################


import operator as _operator

from .sett import Sett as _Sett


class Orderable(_Sett):

    def comparator(self, a, b, /):
        '''Should return `>0` if `a>b`, `<0` if `a<b`, or `0` if `a==b`'''
        gt = self.gt
        return gt(a, b) - gt(b, a)

    gt = _operator.gt

    def __init__(self, /, *args, lbnd=None, ubnd=None, **kwargs):
        self.bnds = self.lbnd, self.ubnd = lbnd, ubnd
        if lbnd is not None:
            self.register_argskwargs(lbnd=lbnd)
        if ubnd is not None:
            self.register_argskwargs(ubnd=ubnd)
        super().__init__(*args, **kwargs)

    def incise_delimit_start(self, incisor, /):
        lbnd, ubnd, comparator = self.lbnd, self.ubnd, self.comparator
        if lbnd is not None:
            if comparator(incisor, lbnd) <= 0:
                return self
        if ubnd is not None:
            if comparator(incisor, ubnd) >= 0:
                incisor = ubnd
        if not self.__contains__(incisor):
            raise KeyError("Delimit out of range")
        return self.new_self(lbnd=incisor)

    def incise_delimit_stop(self, incisor, /):
        lbnd, ubnd, comparator = self.lbnd, self.ubnd, self.comparator
        if lbnd is not None:
            if comparator(incisor, lbnd) <= 0:
                incisor = lbnd
        if ubnd is not None:
            if comparator(incisor, ubnd) >= 0:
                return self
        if not self.__contains__(incisor):
            raise KeyError("Delimit out of range")
        return self.new_self(ubnd=incisor)

    @classmethod
    def slice_start_methods(cls, /):
        yield cls.Element, cls.incise_delimit_start
        yield from super().slice_start_methods()

    @classmethod
    def slice_stop_methods(cls, /):
        yield cls.Element, cls.incise_delimit_stop
        yield from super().slice_stop_methods()

    def item_in_range(self, item):
        lbnd, ubnd, comparator = self.lbnd, self.ubnd, self.comparator
        return all((
            True if lbnd is None else comparator(item, self.lbnd) >= 0,
            True if ubnd is None else comparator(item, self.ubnd) < 0,
            ))

    def __contains__(self, item):
        if not super().__contains__(item):
            return False
        return self.item_in_range(item)


###############################################################################
###############################################################################
