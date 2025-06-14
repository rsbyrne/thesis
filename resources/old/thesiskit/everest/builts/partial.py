from ._callable import Callable

class Partial(Callable):

    _swapscript = '''from everest.builts.partial import Partial as CLASS'''

    def __init__(self, partialClass, **partialInputs):

        self.partialClass, self.partialInputs = partialClass, partialInputs

        super().__init__()

        # Callable attributes:
        self._call_fns.append(self._partial_build)

    def _partial_build(self, *args, **kwargs):
        return self.partialClass(*args, **{**kwargs, **self.partialInputs})
