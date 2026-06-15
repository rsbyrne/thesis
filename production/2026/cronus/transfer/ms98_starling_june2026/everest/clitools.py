###############################################################################
''''''
###############################################################################



import functools as _functools
from collections import abc as _collabc
import argparse as _argparse
import inspect as _inspect
import typing as _typing



CLIMETH_FLAG = "_CLITOOLS_SHELLMETH_FLAG"



class ArgParsingException(ValueError):
    ...



def add_cli(obj, /):
    if callable(obj): add_cli_from_callable(obj)
    elif isinstance(obj, _collabc.Mapping): add_cli_from_namespace(obj)
    else: raise ValueError \
        (f"Cannot build CLI from object of type {type(obj)}!")



def _add_arguments_to_parser(parser, clbl, /):
    
    params = tuple(_inspect.signature(clbl).parameters.values())

    arg_kinds = {}
    used_shorthands = set()
    for param in params:
        anno = param.annotation
        if anno is _inspect._empty:
            raise RuntimeError(
                "Shell-facing methods must be annotated!"
                )
        if isinstance(anno, _typing._AnnotatedAlias):
            anno, paramdoc = anno.__origin__, anno.__metadata__
        else:
            paramdoc = anno.__name__
        param_default = param.default
        if param_default is _inspect._empty:
            param_default = None
            required = True
        else:
            required = False
        if param.kind is param.POSITIONAL_ONLY:
            parser.add_argument(
                param.name,
                type=anno,
                default=param_default,
                help=paramdoc,
                )
            arg_kinds[param.name] = 0
        elif param.kind is param.VAR_POSITIONAL:
            parser.add_argument(
                param.name,
                nargs='*',
                type=anno,
                default=param_default,
                help=paramdoc,
                )
            arg_kinds[param.name] = 1
        elif param.kind is param.KEYWORD_ONLY:
            shorthand = f'-{param.name[0]}'
            if shorthand in used_shorthands:
                raise ValueError(
                    f"Duplicate shorthand forms in shell method signature; "
                    f"ensure all keyword arguments have unique initialisations. "
                    f"(Check `{shorthand}` from method `{param.name}`.)"
                    )
            used_shorthands.add(shorthand)
            if required:
                raise ValueError(
                    "Shell-facing methods may not have mandatory kwargs."
                    )
            if anno is bool:
                parser.add_argument(
                    shorthand, f'--{param.name}',
                    action={
                        False: 'store_true', True: 'store_false'
                        }[param.default],
                    default=param_default,
                    help=paramdoc,
                    )
            else:
                parser.add_argument(
                    shorthand, f'--{param.name}',
                    type=anno,
                    default=param_default,
                    help=paramdoc,
                    )
            arg_kinds[param.name] = 2
        else:
            raise ValueError(
                f"{param.kind} not acceptable as a param kind "
                f"for a shell-facing method."
                )

    return arg_kinds



def _call_callable(args, clbl, arg_kinds, /):
    
    arg_groups = ([], [()], {})
    for key, kind in arg_kinds.items():
        val = getattr(args, key)
        arggrp = arg_groups[kind]
        if kind == 0: arggrp.append(val)
        elif kind == 2: arggrp[key] = val
        else: arggrp[0] = val

    if not hasattr(clbl, CLIMETH_FLAG):
        clbl = shell_method(clbl)
    clbl(
        *arg_groups[0], *arg_groups[1].pop(), **arg_groups[2],
        _shell=True,
        )



def add_cli_from_callable(clbl, /):

    parser = _argparse.ArgumentParser(description=clbl.__doc__)
    arg_kinds = _add_arguments_to_parser(parser, clbl)

    _call_callable(parser.parse_args(), clbl, arg_kinds)



def shell_method(func, /):
    @_functools.wraps(func)
    def wrapped(*args, _shell=False, **kwargs):
        out = func(*args, **kwargs)
        if not _shell: return out
        if isinstance(out, tuple):
            for item in out: print(item)
        else:
            print(out)
    setattr(wrapped, CLIMETH_FLAG, None)
    return wrapped



def add_cli_from_namespace(ns, /):

    modes = tuple(filter(
        lambda item: hasattr(item, CLIMETH_FLAG),
        ns.values(),
        ))

    if not modes:
        raise ValueError("No modes provided for CLI!")

    parser = _argparse.ArgumentParser(description=ns.get(
        '_CLI_DESCRIPTION_', "A Python command line application."
        ))

    mode_parser = parser.add_subparsers(dest='mode', required=True)

    mode_arg_kinds = {}

    used_mode_names = set()
    for clbl, subparser in (
            (clbl, mode_parser.add_parser(
                    nm := clbl.__name__,
                    description=clbl.__doc__,
                    help=clbl.__doc__.split('\n')[0] if clbl.__doc__ else None,
                    )
                )
            for clbl in modes
            ):
        if nm in used_mode_names:
            raise ValueError(f"Duplicate modes! Name: {nm}")
        mode_arg_kinds[nm] = (
            clbl,
            _add_arguments_to_parser(subparser, clbl),
            )
        used_mode_names.add(nm)

    args = parser.parse_args()
    mode = args.__dict__.pop('mode')
    if mode is None: raise ArgParsingException
    try: clbl, arg_kinds = mode_arg_kinds[mode]
    except KeyError as exc: raise ArgParsingException from exc

    _call_callable(args, clbl, arg_kinds)



###############################################################################
'''
An example module:

```
from typing import Annotated
from clitools import *

_CLI_DESCRIPTION_ = "A test app."

@shell_method
def foo(
        *,
        a:Annotated[int, "The base."]=1,
        b:Annotated[int, "The exponent."]=2
        ):
    "Raises `a` to the power of `b`."
    return a**b

if __name__ == '__main__': add_cli(globals())
```
'''
###############################################################################