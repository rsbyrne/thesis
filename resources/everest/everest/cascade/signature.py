###############################################################################
''''''
###############################################################################

import string as _string
import inspect as _inspect
from itertools import zip_longest as _zip_longest
from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache,
    partial as _partial,
    )

from . import _wordhash

from .hierarchy import Hierarchy as _Hierarchy
from .cascade import Cascade as _Cascade

def get_sourcelines(func):
    source = _inspect.getsource(func)
    source = source[:source.index(':\n')]
    lines = source.split('\n')
    line0 = lines[0]
    return [
        line0[line0.index('(')+1:],
        *(line.rstrip() for line in lines[1:]),
        ]

def get_defaults(func):
    params = _inspect.signature(func).parameters
    return {name: p.default for name, p in params.items()}

PLAINCHARS = _string.ascii_lowercase + _string.digits + r'_,=:/\* '

def preprocess_line(line):
    charno = 0
    for charno, char in enumerate(line):
        if char != ' ':
            break
    assert charno % 4 == 0, (charno, line)
    line = line.lstrip(' ')
    return line, charno // 4

def process_line(line, mode):
    clean = ''
    for char in line:
        if mode == '#':
            mode = None
            break
        special = False if char in PLAINCHARS else char
        if mode is None:
            if special:
                mode = special
            else:
                clean += char
        else:
            if special:
                if any((
                        special == ')' and mode == '(',
                        special == ']' and mode == '[',
                        special == '}' and mode == '{',
                        special in ("'", '"') and special == mode,
                        )):
                    mode = None
    return clean, mode

class _IGNORE:
    def __repr__(self):
        return 'IGNORE'
IGNORE = _IGNORE()

def get_paramlevels(func, skip = 0, skipkeys = None, forbiddenkeys = None):

    skipkeys = set() if skipkeys is None else skipkeys
    forbiddenkeys = {} if forbiddenkeys is None else forbiddenkeys

    sourcelines = get_sourcelines(func)

    sig = _inspect.signature(func)
    params = sig.parameters
    if not params:
        return ()

    keys = (key for key in params if not key in skipkeys)
    if skip:
        try:
            for _ in range(skip):
                __ = next(keys)
        except StopIteration as exc:
            raise ValueError(
                "Cannot skip more keys than there are parameters"
                ) from exc
    try:
        key = next(keys)
    except StopIteration: # all parameters were skipped!
        return ()
    mode = None
    paramslist = list()
    indentslist = list()

    for line in sourcelines:

        line, nindents = preprocess_line(line)
        indentslist.append(nindents)

        if line[0] == '#':
            line = line.lstrip('#').strip(' ')
            paramslist.append(line)
            continue

        lineparams = list()
        paramslist.append(lineparams)

        clean, mode = process_line(line, mode)

        for chunk in clean.split(','):
            if key in chunk:
                if key in forbiddenkeys:
                    raise ValueError(f"Forbidden key detected: {key}")
                lineparams.append(params[key])
                try:
                    key = next(keys)
                except StopIteration:
                    break

    if len(indentslist) > 1:
        indent0, indent1, *indentn = indentslist
        indentslist = [
            indent0,
            0,
            *(indent - indent1 for indent in indentn)
            ]

    return list(zip(indentslist, paramslist))

def get_hierarchy(func, /, *, root = None, typ = _Hierarchy, **kwargs):
    if root is None:
        if not issubclass(typ, _Hierarchy):
            raise TypeError(typ)
        hierarchy = typ()
    else:
        hierarchy = root
    currentlev = 0
    addto = hierarchy
    for level, content in get_paramlevels(func, **kwargs):
        while level < currentlev:
            currentlev -= 1
            addto = addto.parent
        if isinstance(content, str):
            if level >= currentlev:
                currentlev += 1
            addto = addto.sub(content)
        else:
            for param in content:
                addto[param.name] = param
    if root is None:
        return hierarchy

def get_cascade(func, **kwargs):
    return get_hierarchy(func, typ = _Cascade, **kwargs)

# def align_args(atup, btup):
#     return tuple(
#         b if a is None else a
#             for a, b in _zip_longest(atup, btup)
#         )

def null_fn():
    ...

@_wordhash.hashable
class Signature(_Cascade):
    _set_locked = False
    signature = None
    inputsskip, inputsskipkeys = None, None
    def __init__(self, parent = null_fn, skip = None, skipkeys = None):
        if isinstance(parent, Signature):
            if (skip is not None) or (skipkeys is not None):
                raise ValueError(
                    "Cannot pass skip arguments to Signature child."
                    )
            super().__init__(parent = parent)
            self.inputsskip, self.inputsskipkeys = \
                parent.inputsskip, parent.inputsskipkeys
            self.signature = parent.signature
        else: # not ischild:
            super().__init__()
            skip = self.inputsskip = \
                0 if skip is None else skip
            skipkeys = self.inputsskipkeys = \
                {} if skipkeys is None else skipkeys
            self.signature = _inspect.signature(parent)
            get_hierarchy(
                parent,
                root = self,
                skip = skip, skipkeys = skipkeys,
                forbiddenkeys = dir(self),
                )
            self.setitem_lock()
    def setitem_lock(self):
        self._set_locked = True
        for sub in self.subs.values():
            sub.setitem_lock()
    def setitem_unlock(self):
        self._set_locked = False
        for sub in self.subs.values():
            sub.setitem_unlock()
    @_lru_cache
    def __getitem__(self, key, /):
        return super().__getitem__(key)
    def __setitem__(self, key, val, /):
        if self._set_locked:
            raise TypeError(
                f"Cannot set item on {type(self)} after initialisation."
                f" {key} = {val}"
                )
        super().__setitem__(key, val)
    def __contains__(self, key, /):
        if super().__contains__(key):
            return True
        for sub in self.subs.values():
            if key in sub:
                return True
        return False
    @_cached_property
    def bind(self):
        return _partial(Bound, self)
    def copy(self):
        raise TypeError(f"Cannot copy object of type={type(self)}")

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

class Bound(Signature):
    bound, partial, args, kwargs = None, None, None, None
    def __init__(self, parent, *args, **kwargs):
        if isinstance(parent, Bound):
            if (args or kwargs):
                raise ValueError("Cannot pass args or kwargs to sub bound.")
            super().__init__(parent)
            self.bound = parent.bound
            self.bind = parent.bind
        else:
            if not isinstance(parent, Signature):
                parent = Signature(parent)
            super().__init__(parent)
            self.bind = _partial(parent.bind, *args, **kwargs)
            self.bound, self.partial, self.args, self.kwargs = \
                get_bound_args_kwargs(
                    parent.signature, parent.inputsskip, parent.inputsskipkeys,
                    args, kwargs
                    )
            self.update(parent)
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
