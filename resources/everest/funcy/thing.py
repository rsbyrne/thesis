from functools import cached_property

from .base import Function
from .exceptions import *

class Thing(Function):
    def evaluate(self):
        return self.prime
    @cached_property
    def value(self):
        return self._evaluate()
