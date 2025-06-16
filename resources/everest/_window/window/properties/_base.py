import weakref
from functools import reduce
import operator

from .exceptions import MissingAsset

class _Kwargs(dict):
    def __init__(self, host, *args, **kwargs):
        self._host = weakref.ref(host)
        super().__init__(*args, **kwargs)
    @property
    def host(self):
        return self._host()
    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        self.host.update()
    def __delitem__(self, key):
        super().__delitem__(key)
        self.host.update()
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.host.update()

class _PropertyController:
    def __init__(self):
        self._masters = list()
        self._subs = dict()
    def _add_sub(self, sub, name):
        self._subs[name] = sub
        setattr(self, name, sub)
        sub._masters.append(weakref.ref(self))
    @property
    def masters(self):
        outs = []
        for ref in self._masters:
            out = ref()
            if not out is None:
                outs.append(out)
        return tuple(outs)
    def update(self):
        for sub in self._subs.values():
            sub.update()
    def __getitem__(self, key):
        return self._subs[key]

class _Vanishable(_PropertyController):
    def __init__(self, *args, visible = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._visible = visible
    @property
    def masterVisible(self):
        masters = self.masters
        for m in masters[::-1]:
            if isinstance(m, _Vanishable):
                v = m.visible
                if not v is None:
                    return v
        return None
    @property
    def visible(self):
        if self._visible is None:
            mv = self.masterVisible
            if mv is None:
                raise ValueError(None)
            return mv
        return self._visible
    @visible.setter
    def visible(self, value):
        self._visible = None if value is None else bool(value)
        self.update()
    def toggle(self):
        self.visible = not self.visible
    def update(self):
        super().update()
        self._set_visible(self.visible)
    def _set_visible(self, value):
        ...

class _Fadable(_PropertyController):
    def __init__(self, *args, alpha = 1., **kwargs):
        super().__init__(*args, **kwargs)
        self._alpha = alpha
    @property
    def masterAlpha(self):
        return reduce(
            operator.mul,
            (1, *(m.alpha for m in self.masters if isinstance(m, _Fadable)))
            )
    @property
    def alpha(self):
        return self._alpha * self.masterAlpha
    @alpha.setter
    def alpha(self, value):
        self._alpha = float(value)
        self.update()
    def update(self):
        super().update()
        self._set_alpha(self.alpha)
    def _set_alpha(self, value):
        ...

class _Colourable(_PropertyController):
    def __init__(self, *args, colour = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._colour = colour
    @property
    def masterColour(self):
        masters = self.masters
        if len(masters):
            for m in masters[::-1]:
                if isinstance(m, _Colourable):
                    c = m.colour
                    if not c is None:
                        return c
        return None
    @property
    def colour(self):
        if self._colour is None:
            c = self.masterColour
        else:
            c = self._colour
        if c is None:
            raise ValueError(None)
        return c
    @colour.setter
    def colour(self, value):
        self._colour = value
        self.update()
    def update(self):
        super().update()
        self._set_colour(self.colour)
    def _set_colour(self, value):
        ...

class _Fillable(_PropertyController):
    def __init__(self, *args, fill = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._fill = fill
    @property
    def masterFill(self):
        masters = self.masters
        if len(masters):
            for m in masters[::-1]:
                if isinstance(m, _Fillable):
                    c = m.fill
                    if not c is None:
                        return c
        return None
    @property
    def fill(self):
        if self._fill is None:
            c = self.masterFill
        else:
            c = self._fill
        if c is None:
            raise ValueError(None)
        return c
    @fill.setter
    def fill(self, value):
        self._fill = value
        self.update()
    def update(self):
        super().update()
        self._set_fill(self.fill)
    def _set_fill(self, value):
        ...

# class _Writable(_PropertyController)