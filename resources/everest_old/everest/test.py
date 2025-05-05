###############################################################################
''''''
###############################################################################

from timeit import timeit, repeat
import numpy as np
import math

def lorenztest():

    def lorenz(x, y, z, s=10, r=28, b=2.667):
        '''
        Given:
           x, y, z: a point of interest in three dimensional space
           s, r, b: parameters defining the lorenz attractor
        Returns:
           x_dot, y_dot, z_dot: values of the lorenz attractor's partial
               derivatives at the point x, y, z
        '''
        x_dot = s*(y - x)
        y_dot = r*x - y - x*z
        z_dot = x*y - b*z
        return x_dot, y_dot, z_dot

    dt = 0.01
    num_steps = 10000

    # Need one more for the initial values
    xs = np.empty(num_steps + 1)
    ys = np.empty(num_steps + 1)
    zs = np.empty(num_steps + 1)

    # Set initial values
    xs[0], ys[0], zs[0] = (0., 1., 1.05)

    def testfn():

        # Step through "time", calculating the partial derivatives at the current point
        # and using them to estimate the next point
        for i in range(num_steps):
            x_dot, y_dot, z_dot = lorenz(xs[i], ys[i], zs[i])
            xs[i + 1] = xs[i] + (x_dot * dt)
            ys[i + 1] = ys[i] + (y_dot * dt)
            zs[i + 1] = zs[i] + (z_dot * dt)

        return xs, ys, zs

    benchmark = timeit(testfn, number = 1)

    from everest.examples.lorenz import Lorenz
    model = Lorenz()
    def testfn():
        model.iterate()
        model.store()
    testval = timeit(testfn, number = num_steps)

    # print(round(testval / benchmark, 2))
    return testval < 10. * benchmark

import unittest
class LorenzTest(unittest.TestCase):
    def test(self):
        self.assertTrue(lorenztest())

if __name__ == '__main__':
    unittest.main()

###############################################################################
''''''
###############################################################################
