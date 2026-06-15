import numpy as np
from planetengine.initials import Channel

class Constant(Channel):

    def __init__(self,
            value = 0.,
            **kwargs
            ):

        super().__init__(**kwargs)

    def evaluate(self, *args):
        return value

CLASS = Constant
