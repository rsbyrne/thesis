###############################################################################
''''''
###############################################################################


import weakref

from .exceptions import MissingAsset
from ._base import _PropertyController, _Vanishable, _Colourable, _Fadable, _Fillable, _Kwargs


class _MplElement(_PropertyController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mplprops = _Kwargs(self)
    @property
    def mplelement(self):
        return self._get_mplelement()
    def _get_mplelement(self):
        raise MissingAsset
    def _update(self):
        self.mplelement.set(**self.mplprops)
        super()._update()
    @property
    def mplprops(self):
        return self._mplprops

class _MplVanishable(_MplElement, _Vanishable):
    def _set_visible(self, value):
        self.mplelement.set_visible(value)

class _MplColourable(_MplElement, _Colourable):
    def _set_colour(self, value):
        self.mplelement.set_color(value)

class _MplFadable(_MplElement, _Fadable):
    def _set_alpha(self, value):
        self.mplelement.set_alpha(value)

class _MplFillable(_MplElement, _Fillable):
    def _set_fill(self, value):
        self.mplelement.set_facecolor(value)

class _MplLinear(_MplVanishable, _MplColourable, _MplFadable):
    ...
class _MplGeometry(_MplLinear, _MplFillable):
    ...

class _MplText(_MplLinear):
    def __init__(self, text = '', **kwargs):
        super().__init__(**kwargs)
        self._text = text
    @property
    def mpltext(self):
        return self.mplelement
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, value):
        self._text = value
        self.update()
    def _update(self):
        self._set_text(self.text)
        super()._update()
    def _set_text(self, value):
        self.mpltext.set_text(value)

###############################################################################
''''''
###############################################################################
