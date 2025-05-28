import numpy as np
from numpy.random import default_rng
from scipy.interpolate import LinearNDInterpolator

from planetengine.initials import Channel
from planetengine import meshutils, mapping



class Noisy(Channel):

    MESHEVAL = True

    def __init__(self,
            factor = 1.2,
            freq = 100.,
            seed = 0,
            prior = None,
            **kwargs
            ):

        self.factor, self.freq, self.seed = factor, freq, seed

        super().__init__(prior=prior, **kwargs)

    def evaluate(self, coordArray, mesh, prior_data):

        factor, freq, seed = self.factor, self.freq, self.seed

        meshUtils = meshutils.get_meshUtils(mesh)
        (xmin, xmax), (ymin, ymax) = meshUtils.scales
        xrange, yrange = xmax - xmin, ymax - ymin
        npoints = int(round(freq**2 * xrange / yrange))

        rng = default_rng(seed)
        randcoords = np.stack(
            (
                rng.standard_normal(npoints) * xrange + xmin,
                rng.standard_normal(npoints) * yrange + ymin,
                ),
            axis=1,
            )
        randdata = rng.uniform(size=len(randcoords)) * 2 - 1

        unboxed = mapping.unbox(mesh, coordArray)

        pertArray = np.nan_to_num(
            LinearNDInterpolator(randcoords, randdata)(*unboxed.transpose())
            ).reshape(len(coordArray), 1)

        return factor ** pertArray * prior_data

CLASS = Noisy
