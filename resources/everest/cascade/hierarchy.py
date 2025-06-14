import inspect
from collections import OrderedDict
from collections.abc import MutableMapping

def remove_prefix(mystr, prefix):
    if mystr.startswith(prefix):
        return mystr[len(prefix):]
    return mystr

def get_callsourcelines(func):
    source = inspect.getsource(func)
    for i, chr in enumerate(source):
        if chr != ' ': break
    assert i % 4 == 0
    indent = ' ' * 4 * (int(i / 4) + 2)
    sourcelines = source.split('\n')
    sourcelines = [line.rstrip() for line in sourcelines]
    callsourcelines = sourcelines[1: sourcelines.index(indent + '):')]
    callsourcelines = [
        remove_prefix(line, indent)
            for line in callsourcelines
        ]
    return callsourcelines

def get_default_func_inputs(func):
    parameters = inspect.signature(func).parameters
    out = parameters.copy()
    if 'self' in out: del out['self']
    for key, val in out.items():
        default = val.default
        if default is inspect.Parameter.empty:
            default = None
        out[key] = default
    argi = 0
    for key, val in parameters.items():
        if str(val)[:1] == '*':
            del out[key]
        # elif str(val)[:1] == '*':
        #     del out[key]
        #     out['arg' + str(argi)] = val
        #     argi += 1
    return OrderedDict(out)

class Hierarchy(OrderedDict):
    def flatten(self):
        return flatten_hierarchy(self)
    def concatenate(self):
        return concatenate_hierarchy(self)
    def remove_ghosts(self):
        for k, v in list(self.items()):
            if k.startswith('_'):
                del self[k]
            elif isinstance(v, type(self)):
                v.remove_ghosts()

def get_hierarchy(func):
    callsourcelines = get_callsourcelines(func)
    defaults = get_default_func_inputs(func)
    hierarchy = Hierarchy()
    level = 0
    prevAddTo = None
    addTo = hierarchy
    for line in callsourcelines:
        indent = level * ' ' * 4
        while not line.startswith(indent):
            level -= 1
            indent = level * ' ' * 4
            addTo = addTo.parent
        line = remove_prefix(line, indent).rstrip(',')
        if line.startswith('#'):
            tag = line[1:].strip()
            level += 1
            newLevel = addTo.setdefault(tag, Hierarchy())
            newLevel.parent = addTo
            addTo = newLevel
        elif not line.startswith(' '):
            try:
                line = line[:line.index('#')].strip()
            except ValueError:
                pass
            line = line.rstrip(',')
            if line in defaults:
                key = line
            else:
                key = line.split('=')[0].strip()
            if not key.startswith('*'):
                addTo[key] = defaults[key]
    return hierarchy

def flatten_hierarchy(hierarchy):
    return OrderedDict(_flatten_hierarchy(hierarchy))
def _flatten_hierarchy(hierarchy):
    for k, v in hierarchy.items():
        if isinstance(v, Hierarchy):
            for sk, sv in _flatten_hierarchy(v):
                yield sk, sv
        else:
            yield k, v

def concatenate_hierarchy(d, parent_key = '', sep = '_'):
    # by Imran@stackoverflow
    items = []
    parent_key = parent_key.strip(sep)
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(concatenate_hierarchy(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return OrderedDict(items)
