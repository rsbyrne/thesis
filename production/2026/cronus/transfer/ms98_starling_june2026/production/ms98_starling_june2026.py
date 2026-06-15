################################################################################
################################################################################


import sys
import os
import math
import itertools
from datetime import datetime

import numpy as np

import planetengine

from campaign import Job

weekno = "week" + str(datetime.today().isocalendar()[1]).zfill(2)

#rng = np.random.default_rng(0)

dims = (
    np.round(10.**np.array([
        5.005, 5.01 , 5.015, 5.02 , 5.025, 5.03 , 5.035, 5.04 , 5.045,
        5.055, 5.06 , 5.065, 5.07 , 5.075, 5.08 , 5.085, 5.09 , 5.095,
        5.105, 5.11 , 5.115, 5.12 , 5.125, 5.13 , 5.135, 5.14 , 5.145,
        5.155, 5.16 , 5.165, 5.17 , 5.175, 5.18 , 5.185, 5.19 , 5.195,
        5.205, 5.21 , 5.215, 5.22 , 5.225, 5.23 , 5.235, 5.24 , 5.245,
        5.255, 5.26 , 5.265, 5.27 , 5.275, 5.28 , 5.285, 5.29 , 5.295,
        5.305, 5.31 , 5.315, 5.32 , 5.325, 5.33 , 5.335, 5.34 , 5.345,
        5.355, 5.36 , 5.365, 5.37 , 5.375, 5.38 , 5.385, 5.39 , 5.395,
        5.405, 5.41 , 5.415, 5.42 , 5.425, 5.43 , 5.435, 5.44 , 5.445,
        5.455, 5.46 , 5.465, 5.47 , 5.475, 5.48 , 5.485, 5.49 , 5.495,
        5.505, 5.515, 5.525, 5.535, 5.545, 5.555, 5.56 , 5.565, 5.57 ,
        5.575, 5.58 , 5.585, 5.59 , 5.595, 5.605, 5.61 , 5.615, 5.62 ,
        5.625, 5.63 , 5.635, 5.64 , 5.645, 5.655, 5.66 , 5.665, 5.67 ,
        5.675, 5.68 , 5.685, 5.69 , 5.695, 5.705, 5.71 , 5.715, 5.72 ,
        5.725, 5.73 , 5.735, 5.74 , 5.745, 5.755, 5.765, 5.775, 5.785,
        5.795, 5.805, 5.81 , 5.815, 5.82 , 5.825, 5.83 , 5.835, 5.84 ,
        5.845, 5.855, 5.86 , 5.865, 5.87 , 5.875, 5.88 , 5.885, 5.89 ,
        5.895, 5.905, 5.91 , 5.915, 5.92 , 5.925, 5.93 , 5.935, 5.94 ,
        5.945, 5.955, 5.96 , 5.965, 5.97 , 5.975, 5.98 , 5.985, 5.99 ,
        5.995
        ])),
    np.round(np.linspace(1., 0.5, 11), 3), # f
    np.round(2. ** np.linspace(0, 1, 11), 3), # aspect
    np.arange(1, 4).astype(float), # freq
    )


with Job(*dims) as job:

    planetengine.set_global_anchor(job.campaignname + '_' + weekno, '.')

    log = job.log

    log(job.campaignname, 'Starting...')

    tauRef, f, aspect, freq = job

    initial = planetengine.initials.Sinusoidal(freq=freq)
    final = (
        planetengine.finals.Averages,
        {'tolerance': 1e-3, 'minlength': 100}
        )

    for res in (64, 128):
        log("Building system for resolution" + str(res) + '...')
        system = planetengine.systems.Viscoplastic(
            res = res,
            temperatureField = initial,
            f = f,
            aspect = aspect,
            tauRef = tauRef,
            innerMethod = 'lu',
            )
        log("Loading...")
        try:
            system.load('max')
        except ValueError:
            log("Nothing to load. Initialising...")
            system.initialise()
        log("Running...")
        system[:final:1000]()
        initial = system
        log("Done.")

    log("We did it!")


################################################################################
################################################################################