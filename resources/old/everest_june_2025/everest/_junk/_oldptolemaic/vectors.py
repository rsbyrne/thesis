###############################################################################
''''''
###############################################################################
from itertools import product
from collections import OrderedDict

from everest import wordhash

def suite_list(**iterables):
    ks, vs = zip(*iterables.items())
    return [
        {k: v for k, v in zip(ks, item)}
            for item in product(*vs)
        ]

class Vector(OrderedDict):
    @property
    def hashID(self):
        return wordhash.w_hash(repr(self))
    @property
    def hashes(self):
        return OrderedDict(
            (k, wordhash.w_hash(v))
                for k, v in self.items()
            )

class VectorSet:
    def __init__(self, **inputSets):
        self.vectors = suite_list(**inputSets)
    def __iter__(self):
        return iter(self.vectors)

class SchemaIterator:
    def __init__(self,
            schema,
            space
            ):
        self.schema = schema
        self.space = space
    def __iter__(self):
        self.space = iter(VectorSet(**self.space))
        return self
    def __next__(self):
        return self.schema(**next(self.space))

###############################################################################
''''''
###############################################################################
