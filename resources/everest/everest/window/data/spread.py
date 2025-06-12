###############################################################################
''''''
###############################################################################
from functools import cached_property
from collections import OrderedDict
from collections.abc import Mapping

from .channel import DataChannel

class DataSpread(Mapping):
    @classmethod
    def convert(cls, d):
        if isinstance(d, cls):
            return d
        return cls(*d)
    def __init__(self,
            x,
            y,
            z = None,
            /,
            c = None,
            s = None,
            l = None,
            ):
        self.x, self.y, self.z = (
            None if d is None else DataChannel.convert(d) for d in (x, y, z)
            )
        self.c, self.s, self.l = (
            None if d is None else DataChannel.convert(d) for d in (c, s, l)
            )
        self.channels = OrderedDict(
            x = self.x,
            y = self.y,
            z = self.z,
            c = self.c,
            s = self.s,
            l = self.l,
            )
        self.vol = not self.z is None
        super().__init__()
    def __getitem__(self, key):
        channels = self.channels
        if isinstance(key, int):
            key = list(channels.keys())[key]
        return channels[key]
    def __iter__(self):
        return iter(self.channels)
    def __len__(self):
        return len(self.channels)
    @property
    def drawArgs(self):
        if self.vol:
            args = (self.x, self.y, self.z)
        else:
            args = (self.x, self.y)
        return tuple(a.data for a in args)
    @property
    def drawKwargs(self):
        out = dict()
        for inKey, outKey in (('c', 'c'), ('s', 's'), ('l', 'label')):
            att = self[inKey]
            if not att is None:
                out[outKey] = att.data
        return out

###############################################################################
''''''
###############################################################################
