import numpy as np
from planetengine.initials import Channel

class Sinusoidal(Channel):

    def __init__(self,
            pert = 0.2,
            freq = 1.,
            phase = 0.,
            **kwargs
            ):

        self.pert, self.freq, self.phase = pert, freq, phase

        super().__init__(**kwargs)

    def evaluate(self, coordArray):
        pert, freq, phase = self.pert, self.freq, self.phase
        valMin, valMax, deltaVal = 0., 1., 1.
        pertArray = \
            pert \
            * np.cos(np.pi * (phase + freq * coordArray[:,0])) \
            * np.sin(np.pi * coordArray[:,1])
        outArray = valMin + deltaVal * (1. - coordArray[:,1]) + pertArray
        outArray = np.clip(outArray, valMin, valMax)
        outArray = np.array([[item] for item in outArray])
        return outArray

CLASS = Sinusoidal
