###############################################################################
''''''
###############################################################################


import ast as _ast
import pickle as _pickle
import fnmatch as _fnmatch

import h5py as _h5py


def resolve_eval(strn):
    out = _ast.literal_eval(strn)
    typout = type(out)
    if issubclass(typout, (list, tuple, frozenset)):
        return typout(resolve(sub) for sub in out)
    return out

stringresmeths = dict(
    _bytes_ = lambda x: pickle.loads(ast.literal_eval(x)),
    _eval_ = resolve_eval,
    _string_ = lambda x: x,
    )

def resolve_str(strn, /):
    for key, meth in stringresmeths.items():
        if strn.startswith(key):
            return meth(strn[len(key):])
    return strn

def resolve_attrs(attrs):
    return {key: resolve(attr) for key, attr in attrs.items()}

def resolve_dataset(dset):
    return dset[()]

def resolve_group(grp):
    out = {key: resolve(item) for key, item in grp.items()}
    out.update(resolve_attrs(grp.attrs))
    return out

resmeths = {
    str: resolve_str,
    _h5py.AttributeManager: resolve_attrs,
    _h5py.Dataset: resolve_dataset,
    _h5py.Group: resolve_group,
    }

def resolve(obj):
    for key, meth in resmeths.items():
        if isinstance(obj, key):
            return meth(obj)
    return obj


def process_query(strn):
    split = strn.split('/')
    if len(split) > 1:
        for sub in split:
            yield from process_query(sub)
    elif isreg(strn):
        yield Reg(strn)
    elif isfnmatch(strn):
        yield FnMatch(strn)
    else:
        yield strn


###############################################################################
###############################################################################
