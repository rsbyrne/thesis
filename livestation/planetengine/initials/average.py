import numpy as np

from planetengine.initials import Channel
from everest.writer import LinkTo

class Average(Channel):

    MESHEVAL = True

    def __init__(self,
            init0,
            init1,
            **kwargs
            ):
        self.init0, self.init1 = init0, init1
        super().__init__(init0 = LinkTo(init0), init1 = LinkTo(init1), **kwargs)

    def evaluate(self, coordArray, mesh):
        init0, init1 = self.init0, self.init1
        if type(init0).MESHEVAL: init0_data = init0.evaluate(coordArray, mesh)
        else: init0_data = init0.evaluate(coordArray)
        if type(init1).MESHEVAL: init1_data = init1.evaluate(coordArray, mesh)
        else: init1_data = init1.evaluate(coordArray)
        return (init0_data + init1_data) / 2

CLASS = Average
