###############################################################################
''''''
###############################################################################

from functools import wraps as _wraps
import inspect as _inspect

from PIL import Image as _PILImage

from .fig import Fig as _Fig


def sort_kwargs(kwargs, clas):
    localkwargs = dict()
    figparams = _inspect.signature(clas).parameters
    for kw in tuple(kwargs):
        if not kw in figparams:
            localkwargs[kw] = kwargs[kw]
            del kwargs[kw]
    return localkwargs, kwargs


class Image(_Fig):
    __slots__ = ('pilargs', 'pilkwargs')
    def __init__(self, *args, **kwargs):
        self.pilargs = args
        self.pilkwargs, kwargs = sort_kwargs(kwargs, _Fig)
        super().__init__(ext = 'png', **kwargs)
    def _update(self):
        ...

class FromFile(Image):
    __slots__ = ('filepath',)
    def __init__(self, filepath, **kwargs):
        self.filepath = filepath
        super().__init__(**kwargs)
    def get_pilimg(self):
        return _PILImage.open(self.filepath, **self.pilkwargs)

class Blank(Image):
    def get_pilimg(self):
        return _PILImage.new(*self.pilargs, **self.pilkwargs)

def pilwraps(pilfunc):
    def decorator(func):
        @_wraps(pilfunc)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

@_wraps(_PILImage.open)
def fromfile(*args, **kwargs):
    return FromFile(*args, **kwargs)
@_wraps(_PILImage.new)
def blank(*args, **kwargs):
    return Blank(*args, **kwargs)

###############################################################################
###############################################################################
