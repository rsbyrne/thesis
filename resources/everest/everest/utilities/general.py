###############################################################################
'''Generally useful code snippets for funcy.'''
###############################################################################

from collections.abc import Mapping as _Mapping
import itertools as _itertools
import os as _os

from .. import abstract as _abstract

RICHOPS = ('lt', 'le', 'eq', 'ne', 'ge', 'gt')
BOOLOPS = ('not', 'truth', 'is', 'is_not',)
ARITHMOPS = (
    'abs', 'add', 'and', 'floordiv', 'index', 'inv',
    'lshift', 'mod', 'mul', 'matmul', 'neg', 'or',
    'pos', 'pow', 'rshift', 'sub', 'truediv', 'xor'
    )
REVOPS = (
    'radd', 'rand', 'rfloordiv', 'rlshift', 'rmod', 'rmul',
    'rmatmul', 'ror', 'rpow', 'rrshift', 'rsub', 'rtruediv',
    'rxor',
    )
SEQOPS = ('concat', 'contains', 'countOf', 'indexOf', )
ALLOPS = (*RICHOPS, *BOOLOPS, *ARITHMOPS, *SEQOPS)

def unpacker_zip(arg1, arg2, /):
    arg1map, arg2map = (isinstance(arg, _Mapping) for arg in (arg1, arg2))
    if arg1map and arg2map:
        arg1, arg2 = zip(*((arg1[k], arg2[k]) for k in arg1 if k in arg2))
        arg1, arg2 = iter(arg1), iter(arg2)
    elif arg1map:
        arg1 = arg1.values()
    elif arg2map:
        arg2 = arg2.values()
    if isinstance(arg1, _abstract.Unpackable):
        if not isinstance(arg2, _abstract.Unpackable):
            arg2 = _itertools.repeat(arg2)
        for sub1, sub2 in zip(arg1, arg2):
            yield from unpacker_zip(sub1, sub2)
    else:
        yield arg1, arg2

def kwargstr(**kwargs):
    outs = []
    for key, val in sorted(kwargs.items()):
        if not type(val) is str:
            try:
                val = val.namestr
            except AttributeError:
                try:
                    val = val.__name__
                except AttributeError:
                    val = str(val)
        outs.append(': '.join((key, val)))
    return '{' + ', '.join(outs) + '}'

def process_scalar(scal):
    return scal.dtype.type(scal)

def add_headers(path, header = '#' * 80, footer = '#' * 80, ext = '.py'):
    path = _os.path.abspath(path)
    for filename in _os.listdir(path):
        subPath = _os.path.join(path, filename)
        if _os.path.isdir(subPath):
            add_headers(subPath)
        filename, extension = _os.path.splitext(filename)
        if extension == ext:
            with open(subPath, mode = 'r+') as file:
                content = file.read()
                file.seek(0, 0)
                if not content.strip('\n').startswith(header):
                    content = f"{header}\n\n{content}"
                if not content.strip('\n').endswith(footer):
                    content = f"{content}\n\n{footer}\n"
                file.write(content)

# def delim_split(seq, /, sep = ...):
#     g = []
#     for el in seq:
#         if el == sep:
#             if g:
#                 if not (len(g) == 1 and g[0] == sep):
#                     yield tuple(g)
#             g.clear()
#         g.append(el)
#     if g:
#         if not (len(g) == 1 and g[0] == sep):
#             yield tuple(g)

###############################################################################
###############################################################################
