from collections.abc import Mapping
from collections import OrderedDict

from .utilities import unpack_tuple, ordered_unpack
from .derived import Derived
from .basevar import Base

class Map(Derived, Mapping):
    def __init__(self, keys, values, /, **kwargs):
        super().__init__(keys, values, **kwargs)
        self._keys = keys
        self._values = values
        self.defaults = dict(zip(self._keys, self._values))
    def evaluate(self):
        return dict(unpack_tuple(*self._resolve_terms()))
    def __getitem__(self, key):
        return self.value[self._value_resolve(key)]
    def __len__(self):
        return len(self.terms[0])
    def __iter__(self):
        yield from self.terms[0]

class SettableMap(Map, Base):
    def __init__(self, keys, values, /, **kwargs):
        values = list(values)
        super().__init__(keys, values, **kwargs)
    def __setitem__(self, key, val):
        for k, v in ordered_unpack(self._keys, key, val).items():
            self._setitem(k, self._process_setitem(v))
        self.update()
        self.refresh()
    def _process_setitem(self, v):
        return v
    def _setitem(self, k, v):
        self._values[self._keys.index(k)] = v
    def reset(self):
        for k in self:
            self[k] = self.defaults[k]

from .variable import Variable, construct_variable

class VarMap(SettableMap):
    def __init__(self, arg1, arg2 = None, /, **kwargs):
        if arg2 is None:
            values = arg1
            keys = tuple(v.name for v in values)
        else:
            keys, values = arg1, arg2
            refined = list()
            for k, v in zip(keys, values):
                if isinstance(v, Variable):
                    if not v.name == k:
                        raise KeyError(v.name, k)
                else:
                    v = construct_variable(v, name = k)
                refined.append(v)
            values = refined
        super().__init__(tuple(keys), tuple(values), **kwargs)
        self.defaults = {k : v.memory for k, v in self.defaults.items()}
    def _setitem(self, k, v):
        self[k].value = v
    def __delitem__(self, k):
        self[k].nullify()
    def nullify(self):
        for k in self:
            del self[k]

class StackMap(VarMap):
    def __init__(self, keys, values, /, **kwargs):
        refined = list()
        for k, v in zip(keys, values):
            if isinstance(v, Variable):
                if not v.name == k:
                    raise KeyError(v.name, k)
            else:
                v = construct_variable(v, name = k, stack = True)
            refined.append(v)
        super().__init__(tuple(keys), tuple(refined), **kwargs)
