###############################################################################
''''''
###############################################################################
from functools import cached_property
from collections import OrderedDict
from collections.abc import Sequence

from .channel import DataChannel
from .spread import DataSpread

# def merge_dicts(d1, d2):
#     for key, val in d2.items():
#         if key not in ('lims', 'capped', 'label', 'i'):
#             if key in d1:
#                 if not d1[key] == val:
#                     raise ValueError("Key clash.")
#                 continue
#             d1[key] = val

class DataPile(Sequence):
    def __init__(self,
            *datas
            ):
        self.datas = list(DataSpread.convert(d) for d in datas)
    @cached_property
    def concatenated(self):
        if len(self.datas) == 1:
            return self.datas[0]
        outs = []
        for dim in ('x', 'y', 'z', 'c', 's', 'l'):
            datas = [d[dim] for d in self.datas]
            datas = [d for d in datas if not d is None]
            if datas:
                allD = datas[0]
                for data in datas[1:]:
                    allD = allD.merge(data)
            else:
                allD = None
            outs.append(allD)
        return DataSpread(*outs)  # pylint: disable=E1120
    def _delself(self):
        try:
            del self.concatenated
        except AttributeError:
            pass
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
    def append(self, arg):
        self.datas.append(arg)
    def align_channel(self, arg, ind):
        if arg is None:
            return arg
        arg = DataChannel.convert(arg)
        conc = self.concatenated[ind]
        if conc is None:
            return arg
        return conc.align(arg)
    def add(self, *args):
        self._delself()
        args = (self.align_channel(arg, ind) for ind, arg in enumerate(args))
        spread = DataSpread(*args)
        self.append(spread)
        self._delself()
        return spread
    def clear(self):
        self.datas.clear()
        self._delself()

###############################################################################
''''''
###############################################################################
