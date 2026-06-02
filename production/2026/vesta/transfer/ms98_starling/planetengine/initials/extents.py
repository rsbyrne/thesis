from underworld import function as fn
import numpy as np
from planetengine.initials import Channel

class Extents(Channel):

    def __init__(self,
            shapes,
            **kwargs
            ):

        polygons = [(0, fn.misc.constant(True))]
        for val, vertices in shapes:
            polygons.append(
                (val, fn.shape.Polygon(vertices))
                )
        self.polygons = polygons

        super().__init__(**kwargs)

    def evaluate(self, coordArray):
        outArray = np.zeros(
            (coordArray.shape[0], 1), dtype = np.int
            )
        for val, polygonFn in self.polygons:
            outArray = np.where(
                polygonFn.evaluate(coordArray),
                val,
                outArray
                )
        return outArray

CLASS = Extents
