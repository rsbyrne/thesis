import numpy as np

import underworld as uw

from everest.builts._applier import Applier
from everest.writer import LinkTo

from ..fieldops import set_scales
from ..fieldops import set_boundaries
from .. import mapping
from ..exceptions import PlanetEngineException

from types import ModuleType



class InitialsException(PlanetEngineException):
    ...



class Configuration(Applier):

    _swapscript = '''from planetengine.initials import Configuration as CLASS'''

    def __init__(self,
            **channels
            ):

        for key, val in sorted(channels.items()):
            if not isinstance(val, Applier):
                raise TypeError

        self.channels = channels

        super().__init__()

        self._apply_fns.append(self._configuration_apply_fn)

    def _configuration_apply_fn(self, obj, mapping = {}):
        for key, val in sorted(self.channels.items()):
            try: toKey = mapping[key]
            except KeyError: toKey = key
            var = obj.locals[toKey]
            val.apply(var)

class Channel(Applier):

    MESHEVAL = False

    def __init__(self,
            boxDims = None,
            tiles = None,
            mirrored = None,
            **kwargs
            ):

        # Expects:
        # self.evaluate

        self.boxDims, self.tiles, self.mirrored = \
            boxDims, tiles, mirrored

        try:
            prior = kwargs.pop('prior')
        except KeyError:
            pass
        else:
            if prior is None:
                prior = Depth()
            self.prior = prior
            kwargs['prior'] = LinkTo(prior)

        super().__init__(supertype = 'Channel', **kwargs)

        self._apply_fns.append(self._channel_apply_fn)

    def _channel_get_data(self, var):
        if type(var) == uw.mesh.MeshVariable:
            mesh, data = var.mesh, var.mesh.data
        elif type(var) == uw.swarm.SwarmVariable:
            mesh, data = var.swarm.mesh, var.swarm.data
        else:
            raise TypeError
        box = mapping.box(
            mesh,
            data,
            boxDims = self.boxDims,
            tiles = self.tiles,
            mirrored = self.mirrored
            )
        args = [box,]
        if type(self).MESHEVAL:
            args.append(mesh)
        try:
            prior = self.prior
        except AttributeError:
            pass
        else:
            if type(prior).MESHEVAL: prior_data = prior.evaluate(box, mesh)
            else: prior_data = prior.evaluate(box)
            args.append(prior_data)
        out = self.evaluate(*args)
        if np.isnan(out.sum()):
            raise InitialsException
        return out

    def _channel_apply_fn(self, var):
        if hasattr(var, 'data'):
            var.data[:] = self._channel_get_data(var)
        elif hasattr(var, 'value'):
            var.value = self.evaluate()
        else:
            raise TypeError
        if hasattr(var, 'scales'):
            set_scales(var, var.scales)
        if hasattr(var, 'bounds'):
            set_boundaries(var, var.bounds)

# Aliases
from .constant import Constant
from .depth import Depth
from .sinusoidal import Sinusoidal
from .copy import Copy
from .extents import Extents
from .conductive import Conductive
from .average import Average
from .postsinusoidal import PostSinusoidal
from .noisy import Noisy