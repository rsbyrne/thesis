import weakref

from .base import Function

class Base(Function):
    # __slots__ = (
    #     'downstream',
    #     )
    def __init__(self, *args, **kwargs):
        self.downstream = weakref.WeakSet()
        super().__init__(*args, **kwargs)
    def register_downstream(self, registrant):
        self.downstream.add(registrant)
    def refresh(self):
        for down in self.downstream:
            down.update()
