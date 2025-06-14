###############################################################################
''''''
###############################################################################


import inspect as _inspect
from functools import (
    lru_cache as _lru_cache,
    partial as _partial,
    )

from .signature import Signature as _Signature, IGNORE


def merge_ignores(skip, skipkeys, args, kwargs):
    args = tuple((
        *(IGNORE for _ in range(skip)),
        *args,
        ))
    for k in kwargs:
        if k in skipkeys:
            raise ValueError(f"Cannot assign skipped key: {k}")
    kwargs = {**{k: IGNORE for k in skipkeys}, **kwargs}
    return args, kwargs


def get_bound_args_kwargs(signature, skip, skipkeys, args, kwargs):
    args, kwargs = merge_ignores(skip, skipkeys, args, kwargs)
    try:
        bound = signature.bind(*args, **kwargs)
        partial = False
    except TypeError:
        bound = signature.bind_partial(*args, **kwargs)
        partial = True
    bound.apply_defaults()
    args = tuple((a for a in bound.args if a is not IGNORE))
    kwargs = {k: v for k, v in bound.kwargs.items() if v is not IGNORE}
    return bound, partial, args, kwargs


class Bound(_Signature):

    __slots__ = ('bound', 'partial', 'args', 'kwargs')

    def __init__(self, parent, *args, **kwargs):
        if isinstance(parent, Bound):
            if (args or kwargs):
                raise ValueError("Cannot pass args or kwargs to sub bound.")
            super().__init__(parent)
            self.bound = parent.bound
            self.bind = parent.bind
            self.args, self.kwargs = (), {}
        else:
            if not isinstance(parent, _Signature):
                parent = _Signature(parent)
            super().__init__(parent)
            self.bind = _partial(parent.bind, *args, **kwargs)
            self.bound, self.partial, self.args, self.kwargs = \
                get_bound_args_kwargs(
                    parent.signature, parent.inputsskip, parent.inputsskipkeys,
                    args, kwargs
                    )
            self.update(parent)
        self.register_argskwargs(*self.args, **self.kwargs)

    @_lru_cache
    def __getitem__(self, key, /):
        out = super().__getitem__(key)
        if isinstance(out, _inspect.Parameter):
            if key in (argus := self.bound.arguments):
                out = argus[key]
                if out is not IGNORE:
                    return out
                raise KeyError
            return out.default
        return out


###############################################################################
###############################################################################
