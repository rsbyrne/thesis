###############################################################################
''''''
###############################################################################
from ._base import _Vanishable, _Colourable, _Fillable, _Fadable
from .edges import Edges
from .grid import Grid
from .ticks import Ticks
from .legend import Legend
from ._element import _MplText, _MplGeometry, _MplVanishable

class _PropsController(_MplVanishable, _Colourable, _Fillable, _Fadable):
    def __init__(self, mplax, **kwargs):
        self.mplax = mplax
        super().__init__(**kwargs)
    def _get_mplelement(self):
        return self.mplax

class AxTitle(_MplText):
    def __init__(self, mplax, **kwargs):
        self.mplax = mplax
        super().__init__(**kwargs)
    def _get_mplelement(self):
        return self.mplax.title

class AxPatch(_MplGeometry):
    def __init__(self, mplax, **kwargs):
        self.mplax = mplax
        super().__init__(**kwargs)
    def _get_mplelement(self):
        return self.mplax.patch
    def _set_colour(self, value):
        self.mplelement.set_edgecolor(value)

class Props(_PropsController):

    def __init__(self,
            mplax,
            outerupdate,
            dims = ('x', 'y'),
            alpha = 1.,
            colour = 'black',
            fill = 'white',
            visible = True,
            title = '',
            ):

        self._outerupdate = outerupdate

        super().__init__(
            mplax,
            alpha = alpha,
            colour = colour,
            visible = visible,
            fill = fill,
            )

        self._add_sub(AxTitle(
            mplax,
            text = title,
            ), 'title')
        self._add_sub(Grid(
            mplax,
            dims = dims,
            colour = 'grey',
            alpha = 0.5,
            ), 'grid')
        self._add_sub(Ticks(
            mplax,
            dims = dims,
            ), 'ticks')
        self._add_sub(Edges(
            mplax,
            dims = dims,
            ), 'edges')
        self._add_sub(Legend(
            mplax,
            visible = False,
            ), 'legend')
        self._add_sub(AxPatch(
            mplax,
            alpha = 0.,
            ), 'patch')

        for dim in dims:
            self['edges'][dim]._add_sub(self['ticks'][dim], 'ticks')
            self['edges'][dim]['primary']._add_sub(self['ticks'][dim], 'ticks')

    def update(self):
        super().update()
        self._outerupdate()

###############################################################################
''''''
###############################################################################
