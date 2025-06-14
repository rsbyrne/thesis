###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod

from .sett import Sett as _Sett
from .orderable import Orderable as _Orderable


class _Originated_(_Orderable):

    metrictype = float

    def comparator(self, a, b):
        o, m = self.origin, self.metric
        return m(o, b) - m(o, a)

    def gt(self, a, b):
        return self.comparator(a, b) > 0

    def pos(self, arg):
        return self.comparator(self.origin, arg)

    def __init__(
            self, /, *args,
            origin=0., lbnd=None, ubnd=None,
            **kwargs
            ):
        if hasattr(self, 'origin'):
            origin = self.origin
        else:
            self.origin = origin
            self.register_argskwargs(origin=origin)
        if lbnd is None:
            lbnd = self.pos(origin)
        elif isinstance(lbnd, self.Element):
            lbnd = self.pos(lbnd)
        ubnd = self.pos(ubnd) if isinstance(ubnd, self.Element) else ubnd
        super().__init__(*args, lbnd=lbnd, ubnd=ubnd, **kwargs)

    def process_relative_metric_incisor(self, incisor):
        lbnd, ubnd = self.bnds
        if incisor > 0:
            try:
                return incisor + lbnd
            except TypeError as exc:
                if lbnd is None:
                    raise IndexError(
                        "Cannot slice from undefined `.lbnd`."
                        ) from exc
                raise TypeError from exc
        elif incisor < 0:
            try:
                return incisor + ubnd
            except TypeError as exc:
                if ubnd is None:
                    raise IndexError(
                        "Cannot slice from undefined `.ubnd`."
                        ) from exc
                raise TypeError from exc
        return incisor

    def process_element_to_metric(self, incisor):
        return self.metrictype(self.pos(incisor))

    def incise_measurable_origin(self, incisor, /):
        raise ValueError("Resetting of origin is forbidden.")

    def incise_metric_start_absolute(self, incisor, /):
        lbnd, ubnd = self.bnds
        incisor = max(lbnd, min(ubnd, incisor))
        if incisor == lbnd:
            return self
        return self.new_self(lbnd=incisor)

    def incise_delimit_start(self, incisor, /):
        incisor = self.process_element_to_metric(incisor)
        return self.incise_metric_start_absolute(incisor)

    def incise_metric_start(self, incisor, /):
        incisor = self.process_relative_metric_incisor(incisor)
        return self.incise_metric_start_absolute(incisor)

    @classmethod
    def slice_start_methods(cls, /):
        yield cls.metrictype, cls.incise_metric_start
        yield from super().slice_start_methods()

    def incise_metric_stop_absolute(self, incisor, /):
        lbnd, ubnd = self.bnds
        incisor = max(lbnd, incisor)
        if ubnd is not None:
            incisor = min(ubnd, incisor)
        if incisor == ubnd:
            return self
        return self.new_self(ubnd=incisor)

    def incise_delimit_stop(self, incisor, /):
        incisor = self.process_element_to_metric(incisor)
        return self.incise_metric_stop_absolute(incisor)

    def incise_metric_stop(self, incisor, /):
        incisor = self.process_relative_metric_incisor(incisor)
        return self.incise_metric_stop_absolute(incisor)

    @classmethod
    def slice_stop_methods(cls, /):
        yield cls.metrictype, cls.incise_metric_stop
        yield from super().slice_stop_methods()

    def item_in_range(self, item):
        pos = self.pos(item)
        return pos >= self.lbnd and pos < self.ubnd


class Measurable(_Sett):

    _Originated_ = _Originated_

    @_abstractmethod
    def metric(self, a, b):
        '''Returns the 'distance' between any two elements.'''
        raise NotImplementedError

    @classmethod
    def child_classes(cls, /):
        yield from super().child_classes()
        yield cls._Originated_, dict(prior=False)

    def incise_measurable_origin(self, incisor, /):
        return self.new_self(cls=self.Originated, origin=incisor)

    @classmethod
    def slice_start_methods(cls, /):
        yield from super().slice_start_methods()
        yield cls.Element, cls.incise_measurable_origin


Originated = Measurable.Originated


# class Reals(Measurable):

#     metrictype = float
#     origin = 0.
#     metric = make_metric()

#     def __init__(self):
#         super().__init__()

# reals = Reals()


###############################################################################
###############################################################################
