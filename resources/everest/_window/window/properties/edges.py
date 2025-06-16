from ._base import _Vanishable, _Colourable, _Fadable
from ._element import _MplText, _MplLinear

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
        for dim in dims:
            sub = EdgeParallels(mplax, dim)
            self._add_sub(sub, dim)
    def swap(self):
        for sub in self._subs.values():
            sub.swap()

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
            swapped = False,
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        self._add_sub(EdgeLabel(mplax, dim), 'label')
        for which in self._whichs:
            self._add_sub(Edge(mplax, dim, which, swapped), which)
        self['primary']._add_sub(self['label'], 'label')
        self._swapped = swapped
        self.dim = dim
        self._label = ''
#         self._lims = None
#         self._scale = 'linear'
#         self._margin = 0.
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
    def swap(self):
        self._swapped = not self.swapped
        self['primary']._swapped = self.swapped
        self['secondary']._swapped = self.swapped
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
    def update(self):
        super().update()
        self._set_side(self.side)
    @property
    def lims(self):
        return self._lims
    @lims.setter
    def lims(self, val):
        self._lims = val
        getattr(self.mplax, f'set_{self.dim}lim')(val)
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, val):
        self._scale = val
        getattr(self.mplax, f'set_{self.dim}scale')(val)
    @property
    def margin(self):
        return self._margin
    @margin.setter
    def margin(self, val):
        self._margin = val
        getattr(self.mplax, f'set_{self.dim}margin')(val)

class Edge(_EdgeController, _MplLinear):
    def __init__(self,
            mplax,
            dim, # 'x', 'y', 'z'
            which, # ('primary', 'secondary')
            swapped = False,
            **kwargs
            ):
        self.dim = dim
        self._swapped = swapped
        self._which = which
        super().__init__(
            mplax,
            **kwargs
            )
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