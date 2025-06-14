from collections import OrderedDict

from .base import Seq
from .seqoperations import muddle
from ..special import unkint
from ..utilities import unpack_tuple

class SeqMap(Seq):
    def __init__(self,
            keys,
            values,
            **kwargs
            ):
        super().__init__(keys, values, **kwargs)
    def _iter(self):
        ks, vs = self._resolve_terms()
        for svs in muddle(vs):
            yield OrderedDict(unpack_tuple(ks, svs))
    def _seqLength(self):
        return unkint
