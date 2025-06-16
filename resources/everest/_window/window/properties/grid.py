from ._base import _Fadable, _Vanishable, _Colourable

class _GridController(_Fadable, _Vanishable, _Colourable):
    def __init__(self, mplax, **kwargs):
        self.mplax = mplax
        super().__init__(**kwargs)

class Grid(_GridController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            alpha = 0.5,
            **kwargs,
            ):
        super().__init__(
            mplax,
            alpha = alpha,
            **kwargs
            )
        for dim in dims:
            sub = GridParallels(mplax, dim)
            self._add_sub(sub, dim)

class GridParallels(_GridController):
    _statures = ('major', 'minor')
    def __init__(self,
            mplax,
            dim, # x, y, z
            **kwargs,
            ):
        super().__init__(
            mplax,
            **kwargs
            )
        for stature in self._statures:
            sub = GridSubs(mplax, dim, stature)
            self._add_sub(sub, stature)

class GridSubs(_GridController):
    def __init__(self,
            mplax,
            dim, # x, y, z
            stature, # major, minor
            alpha = None,
            **kwargs,
            ):
        alpha = dict(major = 1, minor = 0.5)[stature] if alpha is None else alpha
        super().__init__(
            mplax,
            alpha = alpha,
            **kwargs
            )
        self.dim = dim
        self.stature = stature
    def update(self):
        super().update()
        self.mplax.grid(
            b = True,
            axis = self.dim,
            which = self.stature,
            alpha = self.alpha if self.visible else 0.,
            color = self.colour,
            )
    def _set_colour(self, value):
        ...
    def _set_alpha(self, value):
        ...
    def _set_visible(self, value):
        ...