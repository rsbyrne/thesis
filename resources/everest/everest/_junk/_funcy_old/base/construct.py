###############################################################################
''''''
###############################################################################

from .variable import construct_variable as _construct_variable
from .thing import Thing as _Thing
from .slot import Slot as _Slot
from .base import Base as _Base

from .exceptions import BaseConstructFailure

def construct_base(arg = None, /, *args, **kwargs) -> _Base:
    es = []
    try:
        return _construct_variable(arg, *args, **kwargs)
    except BaseConstructFailure as e:
        es.append(e)
    try:
        if arg is None:
            return _Slot._construct(**kwargs)
        elif len(args):
            raise BaseConstructFailure(
                f"Too many args ({len(args) + 1}) provided to base constructor."
                )
        else:
            return _Thing._construct(arg, **kwargs)
    except Exception as e:
        es.append(e)
    raise BaseConstructFailure(
        "Base construct failed"
        f" with args = {(arg, *args)}, kwargs = {kwargs};"
        f" {tuple(es)}"
        )

###############################################################################
''''''
###############################################################################