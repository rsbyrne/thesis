###############################################################################
''''''
###############################################################################

from abc import abstractmethod as _abstractmethod

from . import _Base, _Function, _special, _generic

from .exceptions import *

class Variable(_Base, _generic.Variable):

    open = False
    unique = True

    __slots__ = (
        'stack',
        'memory',
        'pipe',
        'index',
        )

    def __init__(self, *, initVal = None, **kwargs):
        self.memory = initVal
        super().__init__(**kwargs)

    @_abstractmethod
    def rectify(self):
        raise _generic.AbstractMethodException

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
            elif isinstance(val, _Function):
                self.set_pipe(val)
            else:
                try:
                    val._funcy_setvariable__(self)
                except AttributeError:
                    raise TypeError(type(val))
        self.refresh()
    @_abstractmethod
    def set_value(self, val):
        raise _generic.AbstractMethodException

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

    @property
    def isVar(self):
        return True

###############################################################################
''''''
###############################################################################
