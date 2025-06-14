from collections import OrderedDict
from functools import cached_property, lru_cache

from .exceptions import *

class _Fn:
    @cached_property
    def op(self):
        from .ops import ops
        return ops
    # @cached_property
    # def elementop(self):
    #     from .ops import elementops
    #     return elementops
    # @cached_property
    # def seqop(self):
    #     from .ops import seqops
    #     return seqops
    @cached_property
    def base(self):
        from .base import Function
        return Function
    @cached_property
    def var(self):
        from .variable import Variable
        return Variable
    @cached_property
    def slot(self):
        from .slot import Slot
        return Slot
    @cached_property
    def exc(self):
        from ._trier import Trier
        return Trier
    # @cached_property
    # def group(self):
    #     from ._group import Group
    #     return Group
    @cached_property
    def seq(self):
        from .seq.constructor import SeqConstructor
        return SeqConstructor()
    @cached_property
    def thing(self):
        from .thing import Thing
        return Thing
    @cached_property
    def map(self):
        from .map import Map
        return Map
    @cached_property
    def inf(self):
        from .special import inf
        return inf
    @cached_property
    def ninf(self):
        from .special import ninf
        return ninf
    @cached_property
    def null(self):
        from .special import null
        return null
    @cached_property
    def n(self):
        from .seq.nvar import N
        return N()
    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            return self.slot(**kwargs)
        elif len(args) > 1:
            # return self.group(*args, **kwargs)
            raise ValueError
        else:
            arg = args[0]
            if len(kwargs) == 0 and isinstance(arg, self.base):
                if isinstance(arg, self.seq.base):
                    return self.unseq(arg)
                else:
                    return arg
            else:
                try:
                    return self.var.construct_variable(*args, **kwargs)
                except ValueError:
                    return self.thing(*args, **kwargs)
    def __getitem__(self, arg, **kwargs):
        return self.seq(arg, **kwargs)
    @lru_cache
    def __getattr__(self, key):
        for sk in ('op', 'seq'):
            source = getattr(self, sk)
            try:
                return getattr(source, key)
            except AttributeError:
                pass
        raise AttributeError
Fn = _Fn()
