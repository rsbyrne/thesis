from collections import OrderedDict
import inspect

from everest import wordhash

from .hierarchy import get_hierarchy, Hierarchy

def align_inputs(defaults, *args, **kwargs):
    inputs = defaults.copy()
    inputs.update(kwargs)
    for arg, key in zip(args, list(inputs)[:len(args)]):
        if key in kwargs:
            raise ValueError("Two values deduced for key:", key)
        inputs[key] = arg
    return inputs

class Inputs(OrderedDict):
    _hashDepth = 2
    def __init__(self,
            source,
            *args,
            name = None,
            parent = None,
            ignoreLeftovers = False,
            removeGhosts = True,
            **kwargs
            ):
        super().__init__()
        if isinstance(source, Hierarchy):
            hierarchy = source
        elif isinstance(source, type(self)):
            hierarchy = source.hierarchy
        else:
            hierarchy = get_hierarchy(source)
        if removeGhosts:
            hierarchy.remove_ghosts()
        self.hierarchy = hierarchy
        self.subs = []
        self.name = name
        self.parent = parent
        self._ignoreLeftovers = ignoreLeftovers
        for key, val in self.hierarchy.items():
            if key.startswith('_'):
                key = key[1:]
            _ = self._check_key(key)
            if isinstance(val, Hierarchy):
                sub = type(self)(
                    val,
                    name = key,
                    parent = self,
                    ignoreLeftovers = ignoreLeftovers,
                    removeGhosts = removeGhosts,
                    )
                self.subs.append(sub)
                setattr(self, key, sub)
        if parent is None:
            flat = self.hierarchy.flatten()
            self.update(flat)
            new = align_inputs(flat, *args, **kwargs)
            self.update(new)
        else:
            if not ignoreLeftovers:
                assert not len(args)
                assert not len(kwargs)
    def _check_key(self, key):
        if key in dir(self):
            raise ValueError("Cannot use reserved key name:", key)
        return key in self.hierarchy.flatten()
    def __setitem__(self, key, val, caller = None):
        caller = self if caller is None else caller
        if key.startswith('_'):
            key = key[1:]
        check = self._check_key(key)
        if check:
            super().__setitem__(key, val)
            for sub in self.subs:
                if not sub is caller:
                    try:
                        sub.__setitem__(key, val, self)
                    except KeyError:
                        pass
            if not self.parent is None:
                if not self.parent is caller:
                    self.parent.__setitem__(key, val, self)
        elif not self._ignoreLeftovers:
            raise KeyError
        else:
            pass
    def __getattr__(self, key):
        try: return self[key]
        except KeyError: raise AttributeError
    def __setattr__(self, key, val):
        if key in self:
            self[key] = val
        else:
            super().__setattr__(key, val)
    def __repr__(self):
        header = type(self).__name__ + '{' + str(self.name) + '}'
        contentRows = ((k + ' = ' + str(v)) for k, v in self.items())
        content = '(\n    ' + '\n    '.join(contentRows) + '\n    )'
        return header + content
    @property
    def hashID(self):
        return wordhash.get_random_english(
            self._hashDepth,
            seed = repr(self)
            )
    def copy(self, *args, **kwargs):
        return type(self)(self.hierarchy, *args, name = self.name, **kwargs)
