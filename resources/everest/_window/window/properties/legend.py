import weakref

from ._base import _Vanishable, _Colourable, _Fadable, _Fillable, _Kwargs
from ._element import _MplElement, _MplGeometry, _MplText

class _LegendController(_Vanishable, _Colourable, _Fadable, _Fillable):
    def __init__(self, mplax, **kwargs):
        self.mplax = mplax
        super().__init__(**kwargs)

class Legend(_MplElement, _LegendController):
    def __init__(self,
            mplax,
            **kwargs,
            ):
        super().__init__(mplax, **kwargs)
        self._handles, self._labels = [], []
        self._mpllegend = None
        self._kwargs = _Kwargs(self)
        self._add_sub(LegendFrame(self), 'frame')
        self._add_sub(LegendTitle(self), 'title')
    @property
    def kwargs(self):
        return self._kwargs
    def _get_mplelement(self):
        if self._mpllegend is None:
            self._draw()
        return self._mpllegend
    def _draw(self):
        self._mpllegend = self.mplax.legend(
            self.handles,
            self.labels,
            **self.kwargs,
            )
    def _remove(self):
        if not self._mpllegend is None:
            self._mpllegend.remove()
            self._mpllegend = None
    @property
    def mpllegend(self):
        return self.mplelement
    @property
    def mpllabels(self):
        return self.mpllegend.properties()['texts']
    @property
    def handles(self):
        return self._handles
    @handles.setter
    def handles(self, value):
        self._handles.clear()
        if not value is None:
            self._handles.extend(value)
        self.update()
    @property
    def labels(self):
        return self._labels
    @labels.setter
    def labels(self, value):
        self._labels.clear()
        if not value is None:
            self._labels.extend(value)
        self.update()
    def add(self, handle, label):
        self.handles.append(handle)
        self.labels.append(label)
        self.update()
    def update(self):
        handles, labels = self.handles, self.labels
        if not len(handles) == len(labels):
            raise ValueError("Mismatching handles and labels")
        self._remove()
        self._draw()
        super().update()
    def _set_visible(self, value):
        if not len(self.handles):
            value = False
        super()._set_visible(value)
    def _set_colour(self, value):
        for label in self.mpllabels:
            label.set_color(value)
    def set_handles_labels(self, handles, labels):
        self._handles[:] = handles
        self._labels[:] = labels
        self.update()

class _LegendElementController(_MplElement):
    def __init__(self, legend, elementKey, **kwargs):
        self._legendRef = weakref.ref(legend)
        self._elementKey = elementKey
        super().__init__(**kwargs)
    @property
    def _legend(self):
        return self._legendRef()
    def _get_mplelement(self):
        return self._legend.mpllegend.properties()[self._elementKey]

class LegendTitle(_LegendElementController, _MplText):
    def __init__(self, legend, **kwargs):
        super().__init__(legend, 'title', **kwargs)
    def update(self):
        super().update()
        self._legend.mpllegend.set_title(self.text)

class LegendFrame(_LegendElementController, _MplGeometry):
    def __init__(self, legend, **kwargs):
        super().__init__(legend, 'frame', **kwargs)
    def update(self):
        super().update()
        self.mplelement.set_snap(True)
    def _set_colour(self, value):
        self.mplelement.set_edgecolor(value)
