from .base import Function
from .special import null
from .exceptions import *

class Slot(Function):

    open = True

    __slots__ = (
        'slots',
        'argslots',
        'kwargslots',
        )

    def __init__(self, name = None):
        self.slots = 1
        if name is None:
            self.argslots = 1
            self.kwargslots = []
        else:
            self.argslots = 0
            self.kwargslots = [name]
        super().__init__(name = name)
        # raise FuncyException("Cannot close a Slot function.")
    def __call__(self, arg):
        return arg
    def evaluate(self):
        try:
            return self.tempVal
        except AttributeError:
            return null
    @property
    def value(self):
        return self.evaluate()
    def register_downstream(self, registrant):
        # self.downstream.add(registrant)
        pass

    # def evaluate(self):
    #     key = self.name
    #     try:
    #         try:
    #             if key is None:
    #                 return GLOBEKWARGS[key].pop()
    #             else:
    #                 return GLOBEKWARGS[key]
    #         except KeyError:
    #             return GLOBEKWARGS.setdefault(key, GLOBEKWARGS[None].pop())
    #     except IndexError:
    #         return null
