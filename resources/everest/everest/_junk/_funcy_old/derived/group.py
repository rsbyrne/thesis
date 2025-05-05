###############################################################################
''''''
###############################################################################

from . import _generic, _Gruple, _unpacker_zip
from .derived import Derived as _Derived

def groups_resolve(obj):
    if isinstance(obj, Group):
        yield (groups_resolve(t) for t in obj.terms)
    else:
        yield obj

class Group(_Derived, _generic.Struct):

    def _evaluate(self, terms):
        return _Gruple(terms)

    @property
    def rawValue(self) -> _Gruple:
        return self._contents

    def _plain_getitem(self, ind: _generic.ShallowIncisor, /) -> object:
        return self.terms[self._value_resolve(ind)]
    def __setitem__(self, ind: _generic.ShallowIncisor, val: object, /):
        got = self._plain_getitem(ind)
        if isinstance(got, _generic.Variable):
            got.value = val
        else:
            for t, v in _unpacker_zip(iter(got), val):
                t.value = v
    def __delitem__(self, ind: _generic.ShallowIncisor):
        self[ind] = None

    def __len__(self):
        return len(self.terms)

###############################################################################
''''''
###############################################################################
