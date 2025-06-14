import math
import importlib

def prettify_nbytes(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

import numbers
import numpy as np

def make_scalar(arg):
    if isinstance(arg, np.ndarray):
        if len(arg.shape):
            if any(i > 1 for i in arg.shape):
                raise ValueError(
                    "Array-like input must have only one entry: shape was ",
                    arg.shape
                    )
            for i in arg.shape:
                arg = arg[i]
        else:
            arg = arg.item()
    else:
        pass
    if not issubclass(type(arg), numbers.Number):
        raise ValueError(arg, type(arg))
    return arg

def get_object_from_module(qualname):
    *prenames, lastname = qualname.split('.')
    module = importlib.import_module('.'.join(prenames))
    return getattr(module, lastname)

def get_owner(obj):
    out = importlib.import_module(obj.__module__)
    for n in obj.__qualname__.split('.'):
        out = getattr(out, n)
    return out

def inner_class(*bases):
    def _inner_class(cls):
        bs = []
        for b in bases:
            try: bs.append(getattr(b, cls.__name__))
            except AttributeError: pass
        bs = sorted(set(bs), key = bs.index)
        return type(cls)(
            cls.__name__,
            (cls, *bs),
            {}
            )
    return _inner_class
