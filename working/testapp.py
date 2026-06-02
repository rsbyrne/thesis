from aliases import *
from typing import Annotated
from everest.clitools import *

_CLI_DESCRIPTION_ = "A test app."

@shell_method
def foo(
        *,
        a:Annotated[int, "The base."]=2,
        b:Annotated[int, "The exponent."]=3,
        ):
    "Raises `a` to the power of `b`."
    return a**b

if __name__ == '__main__': add_cli(globals())