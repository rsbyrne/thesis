import numpy as np
from planetengine.initials import Channel

class Depth(Channel):

    def evaluate(self, coordArray):
        return (1. - coordArray[:, 1]).reshape(coordArray.shape[0], 1)

CLASS = Depth
