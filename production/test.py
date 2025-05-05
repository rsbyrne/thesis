################################################################################


if __name__ != '__main__':
    raise RuntimeException

import numpy as np

from campaign import Job


dims = (
    np.round(10. ** np.linspace(0, 5, 11), 3), # etaDelta
    np.round(np.linspace(1., 0.5, 11), 3), # f
    np.round(2. ** np.linspace(0, 1, 11), 3), # aspect
    np.array([0., *np.round(10 ** np.linspace(-2, 1, 13), 3)]), # H
    )

print(dims)

with Job(*dims) as job:

    log = job.log

    log(job.campaignname, 'Starting...')

    log("We did it!")


################################################################################
