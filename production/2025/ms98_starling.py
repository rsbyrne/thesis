################################################################################
# ###############################################################################


import sys
import os
import math
import itertools
from datetime import datetime

import numpy as np

import planetengine
import everest

from campaign import Job

dims = (
    np.arange(0, 1000), # seed
    np.arange(0, 1000000), # iteration
    np.round(np.linspace(1., 0.5, 11), 3), # f
    np.round(2. ** np.linspace(0, 1, 11), 3), # aspect
#     np.arange(1, 6).astype(float), # freq
    )

weekno = "week_" + str(datetime.today().isocalendar()[1]).zfill(2)

with Job(*dims) as job:

    log = job.log

    log(job.campaignname, 'Starting...')

#     seed, iteration, f, aspect, freq = job
    seed, iteration, f, aspect = job

    rand = np.random.default_rng(seed).random(1000000)[iteration]
    tauRef = np.round(10**(5 + rand), 3)

    planetengine.set_global_anchor(
        job.campaignname + "_" + weekno,
        '.',
        )

#     log("Creating initial...")
#     initial = planetengine.initials.Sinusoidal(freq=freq)

    log("Creating final...")
    final = (
        planetengine.finals.Averages,
        {'tolerance': 1e-3, 'minlength': 100}
        )

    log("Creating first pass system...")
    system = planetengine.systems.Viscoplastic(
        tauRef = tauRef,
        f = f,
        aspect = aspect,
        res = 64,
        observers = True,
#         temperatureField = initial,
        innerMethod = 'lu',
        )

    log("Running first pass system...")
    system.initialise()
    system[:final:1000]()

#     log("Creating second pass system...")
#     system = plantengine.systems.Viscoplastic(
#         tauRef = tauRef,
#         f = f,
#         aspect = aspect,
#         res = 128,
#         observers = True,
#         temperatureField = system,
#         innerMethod = 'lu',
#         )

#     log("Running second pass system...")
#     system[:final:100]()

    log("We did it!")


################################################################################
# ###############################################################################
