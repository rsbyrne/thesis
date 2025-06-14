from everest.builts import Built

class Noise(Built):

    'genus' = 'noise'

    def __init__(
            self
            ):
        self.preditherings = dict()
        self.system = None
        super().__init__()

    def attach(self, system):
        self.system = system
        self._attach(system)
    def _attach(*args):
        pass

    def __enter__(self):
        system = self.system
        for i, (vn, var) in enumerate(sorted(system.varsOfState.items())):
            self.preditherings[var] = var.data.copy()
            self.apply(var, (system.count.value, i))
        system.clipVals()
        system.setBounds()

    def __exit__(self, *args):
        system = self.system
        exc_type, exc_value, tb = args
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
        for var in system.varsOfState.values():
            var.data[:] = self.preditherings[var]
            del self.preditherings[var]
        return True
