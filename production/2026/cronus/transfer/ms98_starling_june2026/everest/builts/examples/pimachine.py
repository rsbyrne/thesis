import numpy as np

from everest.builts._iterator import Iterator

class PiMachine(Iterator):
    # Implements the Bailey-Borwein-Plouffe formula;
    # default args yield pi.
    def __init__(
            self,
            s : int = 1,
            b : int = 16,
            A : list = [4, 0, 0, -2, -1, -1, 0, 0],
            **kwargs
            ):
        self.state = 0.
        self._outkeys = ['pi,']
        super().__init__(**kwargs)
    def kth(self, k):
        s, b, A = self.inputs['s'], self.inputs['b'], self.inputs['A']
        val = 1. / b **k * sum([
            a / (len(A) * k + (j + 1))**s \
                for j, a in enumerate(A)
            ])
        return val
    def _out(self):
        yield np.array(self.state)
    def _initialise(self):
        self.state = self.kth(0)
    def _iterate(self):
        kthVal = self.kth(self.count.value)
        self.state += kthVal
    def _load(self, loadDict):
        self.state = loadDict['pi']

CLASS = PiMachine
