###############################################################################
''''''
###############################################################################

from .group import Group as _Group
from .map import Map as _Map
from .slyce import Slyce as _Slyce

from .exceptions import *

def construct_derived(arg = None, /, *args, **kwargs):
    if arglen := len(args): # i.e. there are multiple args
        return _Group._construct(arg, *args, **kwargs)
    else: # i.e. only one arg
        if (argType := type(arg)) is tuple:
            return _Group._construct(*arg, **kwargs)
        elif argType is dict:
            return _Map._construct(
                arg.keys(), arg.values()
                )
        elif argType is set:
            raise NotYetImplemented
        elif argType is slice:
            return _Slyce._construct(
                arg.start, arg.stop, arg.step
                )
        else:
            raise ConstructFailure

###############################################################################
''''''
###############################################################################
