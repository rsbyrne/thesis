import numpy as np

from campaign import run

raise Exception

with run(
        np.round(10. ** np.linspace(0, 5, 11), 3), # etaDelta
        np.round(np.linspace(1., 0.5, 11), 3), # f
        np.round(2. ** np.linspace(0, 1, 11), 3), # aspect
        np.array([0., *np.round(10 ** np.linspace(-2, 1, 13), 3)]), # H
        ) as job:

    job.log([*job])
    raise ValueError