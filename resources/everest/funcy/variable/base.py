from ..basevar import Base
from ..base import Function
from ..special import null
from .exceptions import *

class Variable(Base):

    open = False

    __slots__ = (
        'stack',
        'memory',
        'pipe',
        )

    def __init__(self,
            *args,
            _initVal = null,
            **kwargs,
            ):
        self.memory = _initVal
        super().__init__(*args, **kwargs)
        try:
            self.rectify = lambda: None
        except:
            pass

    @property
    def value(self):
        self.rectify()
        return self.memory
    @value.setter
    def value(self, val):
        try:
            self.set_value(val)
        except TypeError:
            if val is Ellipsis:
                return
            elif isinstance(val, Function):
                self.set_pipe(val)
            else:
                try:
                    val._funcy_setvariable__(self)
                except AttributeError:
                    raise TypeError(type(val))
        self.refresh()
    def set_value(self, val):
        raise MissingAsset

    def add_stack(self):
        from .stack import Stack
        try:
            shape = self.shape
        except AttributeError:
            shape = ()
        self.stack = Stack(shape, self.dtype)
    def store(self):
        try:
            self.stack.append(self.memory)
        except AttributeError:
            self.add_stack()
            self.stack.append(self.memory)
    @property
    def stored(self):
        try:
            return self.stack.value
        except AttributeError:
            self.add_stack
            return self.stack.value

    def set_pipe(self, func):
        self.pipe = func
        self.pipe.downstream.add(self)
        self.update = self._pipe_update

    def _pipe_update(self):
        self.value = self.pipe.value
