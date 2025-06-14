###############################################################################
''''''
###############################################################################
from ._base import _Vanishable, _Colourable, _Fadable
from ._element import _MplText, _MplLinear
from .ticks import Ticks

class _EdgeController(_Vanishable, _Colourable, _Fadable):
    _directions = dict(
        x = ('bottom', 'top'),
        y = ('left', 'right'),
        z = ('front', 'back'),
        )
    def __init__(self, mplax, **kwargs):
        self.mplax = mplax
        super().__init__(**kwargs)

class Edges(_EdgeController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        self._dims = dims
        ticks = Ticks(mplax, dims=dims)
        self._add_sub(ticks, 'ticks')
        for dim in dims:
            self._add_sub(
                EdgeParallels(mplax, dim, ticks[dim]),
                dim
                )
    def swap(self):
        for dim in self._dims:
            self[dim].swap()

class EdgeLabel(_MplText):
    def __init__(self, mplax, dim, **kwargs):
        self.mplax = mplax
        self.dim = dim
        super().__init__(**kwargs)
    @property
    def mplaxAxis(self):
        return getattr(self.mplax, f'{self.dim}axis')
    def _get_mplelement(self):
        return self.mplaxAxis.label

class EdgeParallels(_EdgeController):
    _whichs = ('primary', 'secondary')
    def __init__(self,
            mplax,
            dim, # 'x', 'y', 'z'
            ticks,
            swapped = False,
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        self._add_sub(ticks, 'ticks')
        label = EdgeLabel(mplax, dim)
        self._add_sub(label, 'label')
        for which in self._whichs:
            primary = which == 'primary'
            self._add_sub(
                Edge(
                    mplax, dim, which, primary, swapped,
                    (ticks if primary else None),
                    (label if primary else None),
                    ),
                which
                )
        self._swapped = swapped
        self.dim = dim
        self._label = ''
        self._lims = None
        self._scale = 'linear'
#         self._margin = 0.
    def _lock_to(self, other, /):
        self._lims = other.lims
        self._scale = other.scale
#         self.margin = other.margin
        self.ticks._lock_to(other.ticks)
    def lock_to(self, other, /):
        self._lock_to(other)
        self.update()
    @property
    def side(self):
        return self['primary'].side
    @property
    def swapped(self):
        return self._swapped
    @swapped.setter
    def swapped(self, value):
        if value != self.swapped:
            self.swap()
    def _swap(self):
        self._swapped = not self.swapped
        self['primary']._swapped = self.swapped
        self['secondary']._swapped = self.swapped
    def swap(self):
        self._swap()
        self.update()
    @property
    def mplaxAxis(self):
        return getattr(self.mplax, f'{self.dim}axis')
#     def _set_label(self, *args, **kwargs):
#         getattr(self.mplax, f'set_{self.dim}label')(*args, **kwargs)
    def _set_side(self, side):
        try:
            getattr(self.mplaxAxis, f'tick_{side}')()
            self.mplaxAxis.set_label_position(side)
        except AttributeError: # we assume it's 3d
            pass
    @property
    def lims(self):
        return self._lims
    @lims.setter
    def lims(self, val):
        self._lims = val
        self.update()
    def _set_lims(self, lims):
        getattr(self.mplax, f'set_{self.dim}lim')(lims)
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, val):
        self._scale = val
        self.update()
    def _set_scale(self, scale):
        getattr(self.mplax, f'set_{self.dim}scale')(scale)
    def _update(self):
        self._set_side(self.side)
        self._set_lims(self.lims)
        self._set_scale(self.scale)
        super()._update()

#     @property
#     def margin(self):
#         return self._margin
#     @margin.setter
#     def margin(self, val):
#         self._margin = val
#         getattr(self.mplax, f'set_{self.dim}margin')(val)

class Edge(_EdgeController, _MplLinear):
    def __init__(self,
            mplax,
            dim, # 'x', 'y', 'z'
            which, # ('primary', 'secondary')
            primary=None,
            swapped=False,
            ticks=None,
            label=None,
            **kwargs
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        self.dim = dim
        self._swapped = swapped
        self._which = which
        if ticks is not None:
            self._add_sub(ticks, 'ticks')
        if label is not None:
            self._add_sub(label, 'label')
    def _get_mplelement(self):
        return self.mplax.spines[self.side]
    @property
    def side(self):
        return self._directions[self.dim][
            dict(primary = 0, secondary = 1)[self._which] ^ self.swapped
            ]
    @property
    def swapped(self):
        return self._swapped

# class Spine(_SpineController):
#     def __init__(self,
#             mplax,
#             side,
#             **kwargs,
#             ):
#         super().__init__(
#             mplax,
#             (side,),
#             **kwargs
#             )
#     @property
#     def spine(self):
#         return self.mplax
###############################################################################
''''''
###############################################################################
