import numpy as np
from planetengine.initials import Channel
from planetengine.initials.depth import Depth
from everest.writer import LinkTo

class PostSinusoidal(Channel):

    MESHEVAL = True

    def __init__(self,
            factor = 2.,
            freq = 1.,
            phase = 0.,
            prior = None,
            **kwargs
            ):

        self.factor, self.freq, self.phase = factor, freq, phase

        super().__init__(prior=prior, **kwargs)

    def evaluate(self, coordArray, mesh, prior_data):
        factor, freq, phase = self.factor, self.freq, self.phase
        xcoords, ycoords = coordArray.transpose()
        depth = 1 - ycoords
        pertArray = \
              np.cos(np.pi * (phase + freq * xcoords)) \
            * np.sin(np.pi * ycoords)  # +1.0 to -1.0 in middle of domain
        data = factor ** pertArray * prior_data.flatten()
        return data.reshape(coordArray.shape[0], 1)

CLASS = PostSinusoidal
