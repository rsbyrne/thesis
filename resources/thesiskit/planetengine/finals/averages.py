import numpy as np

from window import analysis

from planetengine.finals import Final
from planetengine.observers import Thermo

class Averages(Final):

    def __init__(self,
            system,
            observerClass = Thermo,
            observerKwargs = dict(),
            freq = 10,
            x = 'chron',
            y = ('Nu', 'theta_av'),
            tolerance = 1e-2,
            horizon = 1. / 2. ** 0.5,
            depth = 3,
            check = 50,
            minlength = 50
            ):

        self.system = system
        self.observer = self.system.add_observer(
            observerClass,
            **observerKwargs
            )
        ignoreme = self.observer.add_freq(freq)
        self.x = x
        self.y = y if type(y) is tuple else (y,)
        self.tolerance = tolerance
        self.horizon = horizon
        self.minlength = minlength
        self.depth = depth

        super().__init__(check = check)

    def _zone_fn(self):
        chron = self.observer.data[self.x]
        metrics = self.observer.data[self.y]
        if len(chron) > self.minlength:
            return all([self._final_condition(chron, m) for m in metrics])
        else:
            return False

    def _final_condition(self, chron, metric):
        chron, metric = analysis.time_smooth(chron, metric, sampleFactor = 2.)
        chron, metric = chron[1:-1], metric[1:-1]
        avs = []
        for i in range(self.depth):
            cutoff = np.max(chron) - self.horizon ** (i + 1) * np.ptp(chron)
            avs.append(np.average(metric[np.where(chron > cutoff)]))
        return max(avs) / min(avs) <= 1. + self.tolerance

CLASS = Averages
