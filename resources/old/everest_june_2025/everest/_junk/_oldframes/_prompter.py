###############################################################################
''''''
###############################################################################
import weakref
from functools import wraps

from . import Frame
# from ._promptable import Promptable
from ..exceptions import *
from ..weaklist import WeakList

class PrompterException(EverestException):
    pass
class PrompterTypeError(TypeError, PrompterException):
    pass
class PrompterRegistryError(PrompterException):
    pass

def _producer_update_outs(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        toReturn = func(self, *args, **kwargs)
        self._update_randomstate()
        return toReturn
    return wrapper

def _prompter_prompt_all(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        toReturn = func(self, *args, **kwargs)
        self.promptees.prompt()
        return toReturn
    return wrapper

class Promptees:
    def __init__(self, host):
        self.promptees = WeakList()
        self._host = weakref.ref(host)
        super().__init__()
    @property
    def host(self):
        host = self._host()
        assert not host is None
        return host
    def add(self, arg, silent = False):
        # if not isinstance(arg, Promptable):
        #     raise PrompterTypeError
        if arg in self.promptees:
            if not silent:
                raise PrompterRegistryError
        else:
            self.promptees.append(arg)
    def remove(self, arg, silent = False):
        if not arg in self.promptees:
            if not silent:
                raise PrompterRegistryError
        else:
            self.promptees.remove(arg)
    def prompt(self):
        for promptee in self.promptees:
            promptee.prompt(self.host)
    def __repr__(self):
        return str(self.promptees)

class Prompter(Frame):

    def __init__(self,
            **kwargs
            ):

        self.promptees = Promptees(self)

        super().__init__(**kwargs)

###############################################################################
''''''
###############################################################################
