###############################################################################
''''''
###############################################################################
from functools import cached_property
from collections import OrderedDict
from collections.abc import MutableSequence

import numpy as np

from ..utilities import unique_list
from .channel import DataChannel
from .spread import DataSpread

class DataPile(MutableSequence):
    def __init__(self,
            *datas
            ):
        self.datas = list(DataSpread.convert(d) for d in datas)
    @cached_property
    def concatenated(self):
        outs = []
        for dim in ('x', 'y', 'z', 'c', 's', 'l'):
            datas = [d[dim] for d in self.datas]
            datas = [d for d in datas if not d is None]
            if datas:
                minLim, minCapped = sorted(
                    [(d.lims[0], d.capped[0]) for d in datas],
                    key = lambda d: d[0]
                    )[0]
                maxLim, maxCapped = sorted(
                    [(d.lims[1], d.capped[1]) for d in datas],
                    key = lambda d: d[0]
                    )[-1]
                allLabel = ', '.join(unique_list(
                    [d.label for d in datas], lambda e: len(e)
                    ))
                allD = DataChannel(
                    np.concatenate([d.data for d in datas]),
                    lims = (minLim, maxLim),
                    capped = (minCapped, maxCapped),
                    label = allLabel,
                    )
            else:
                allD = None
            outs.append(allD)
        return DataSpread(*outs)
    def _delself(self):
        try: del self.concatenated
        except AttributeError: pass
    def __getitem__(self, key):
        return self.datas.__getitem__(key)
    def __setitem__(self, key, val):
        self._delself()
        self.datas.__setitem__(key, val)
    def __delitem__(self, key):
        self._delself()
        self.datas.__delitem__(key)
    def __len__(self):
        return len(self.datas)
    def insert(self, index, object):
        self._delself()
        self.datas.insert(index, DataSpread.convert(object))

###############################################################################
''''''
###############################################################################
