from functools import wraps
import numpy as np
from collections import OrderedDict

from everest.window import Canvas, Data

from everest.frames._traversable import Traversable
from everest.frames._stateful import StateVar
from everest.frames._chronable import Chronable
from everest.frames._iterable import _iterable_initialise_if_necessary
from grouper import Grouper

from ..exceptions import *

from ..array import swarm_split

colourCodes = dict(zip(
    ['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'brown', 'pink', 'grey'],
    [1. / 18. + i * 1. / 9 for i in range(0, 9)],
    ))

class SwarmVar(StateVar):
    def __init__(self, var, name, params):
        assert isinstance(var, np.ndarray)
        super().__init__(var, name = name)
        self.params = params
    def _set_value(self, fromVar):
        if type(fromVar) is type(self):
            assert not fromVar is self
            self.data[...] = swarm_split(
                fromVar.data,
                (fromVar.params.corner, self.params.corner),
                (fromVar.params.aspect, self.params.aspect),
                (fromVar.params.scale, self.params.scale),
                self.params.popDensity,
                spatialDecimals = self.params.spatialDecimals
                )
        else:
            super()._set_value(fromVar)
class GlobeVar(StateVar):
    def __init__(self, var, name, params):
        super().__init__(var, name = name)
        self.params = params

def _constructed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_locals'):
            self.construct()
        return func(self, *args, **kwargs)
    return wrapper

class System(Chronable, Traversable):

    reqAtts = {
        'initialise',
        'iterate',
        '_update',
        'nAgents',
        'minCoords',
        'maxCoords',
        'susceptible',
        }
    configsKeys = (
        'agentCoords',
        'indicated',
        'recovered',
        'timeIndicated',
        )
    reqAtts.update(configsKeys)

    def __init__(self,
            **kwargs
            ):
        super().__init__(
            **kwargs
            )
        self._figUpToDate = False

    @property
    def locals(self):
        try:
            return self._locals
        except AttributeError:
            self.construct()
            return self._locals
    def construct(self):
        constructed = self._construct(p = self.inputs)
        localObj = Grouper(constructed)
        del localObj['p']
        try: del localObj['self']
        except KeyError: pass
        self._construct_check(localObj)
        self._locals = localObj
        self._stateVars = list()
        for k in self.configs.keys():
            var = self._locals[k]
            if isinstance(var, np.ndarray):
                var = SwarmVar(var, k, self.inputs)
            else:
                var = GlobeVar(var, k, self.inputs)
            self._stateVars.append(var)
    @classmethod
    def _construct_check(cls, obj):
        missing = [att for att in cls.reqAtts if not hasattr(obj, att)]
        if len(missing):
            raise MissingAsset(
                "User must provide the following: " + '; '.join(missing)
                )

    @_constructed
    def _state_vars(self):
        for o in super()._state_vars(): yield o
        for v in self._stateVars: yield v

    @_constructed
    def _initialise(self):
        super()._initialise()
        self._locals.initialise()
    def _iterate(self, **kwargs):
        dt = self._locals.iterate()
        self.indices['chron'] += dt
        super()._iterate(**kwargs)

    def _save(self):
        super()._save()
        self.update()

    @_constructed
    def _stop(self):
        return super()._stop() or self._locals.stop()

    def update(self):
        self._locals._update()
        self._figUpToDate = False

    def _iterable_changed_state_hook(self):
        super()._iterable_changed_state_hook()
        self.update()

    def _make_fig(self):
        xs, ys = self._locals.agentCoords.transpose()
        nMarkers = self._locals.nAgents
        cs = np.random.rand(nMarkers)
        hypot = max(7, self.inputs.scale)
        aspect = self.inputs.aspect
        vert = hypot / np.sqrt((aspect ** 2 + 1))
        width = vert * aspect
        figsize = (round(width, 1), round(vert, 1))
        canvas = Canvas(size = figsize)
        ax = canvas.make_ax()
        ax.scatter(
            Data(
                xs,
                lims = (self._locals.minCoords[0], self._locals.maxCoords[0]),
                capped = (True, True),
                label = 'x km',
                ),
            Data(
                ys,
                lims = (self._locals.minCoords[1], self._locals.maxCoords[1]),
                capped = (True, True),
                label = 'y km'
                ),
            cs,
            )
        ax.ax.set_facecolor('black')
        collection = ax.collections[0]
        collection.set_alpha(1.)
        collection.set_cmap('Set1')
        collection.autoscale()
        return canvas
    @property
    @_iterable_initialise_if_necessary(post = True)
    def fig(self):
        if not hasattr(self, '_fig'):
            self._fig = self._make_fig()
        if not self._figUpToDate:
            self._update_fig()
        return self._fig
    def _update_fig(self):
        global colourCodes
        step = self.indices['count']
        indicated = self._locals.indicated
        susceptible = self._locals.susceptible
        recovered = self._locals.recovered
        coords = self._locals.agentCoords
        nMarkers = self._locals.nAgents
        figarea = self._fig.size[1] ** 2 * self.inputs.aspect
        cs = np.zeros(nMarkers)
        cs[...] = colourCodes['grey']
        cs[susceptible] = colourCodes['blue']
        cs[indicated] = colourCodes['red']
        cs[recovered] = colourCodes['yellow']
        figareaPoints = figarea * 72 ** 2
        s = figareaPoints / nMarkers * 0.1
        ss = np.full(nMarkers, s)
        ss[indicated] *= 4
        canvas = self._fig
        ax = canvas.axes[0][0][0]
        collection = ax.collections[0]
        collection.set_offsets(
            np.concatenate([coords[~indicated], coords[indicated]])
            )
        collection.set_array(
            np.concatenate([cs[~indicated], cs[indicated]])
            )
        collection.set_sizes(
            np.concatenate([ss[~indicated], ss[indicated]])
            )
        ax.set_title(f'Step: {step.valstr}')
        self._figUpToDate = True
    def show(self):
        return self.fig.fig

    @property
    def count(self):
        return self.indices['count']
    @property
    def chron(self):
        return self.indices['chron']
