################################################################################


import sys
import os
import math
import itertools

import numpy as np

import planetengine
import everest

from campaign import get_job, get_logger


CAMPAIGNNAME, LOGPATH, COUNTER, *SLICE = sys.argv[1:]

planetengine.set_global_anchor(CAMPAIGNNAME, '.')

with open(LOGPATH, mode = 'r+') as logfile:

    log = get_logger(logfile)

    log(CAMPAIGNNAME, LOGPATH, ', '.join(SLICE), COUNTER)

    log("Getting job...")
    inputs = dict()
    dims = (
        [1.,0.9,0.8,0.7,0.6,0.5], # f
        [1.,1.414], # aspect
        [0.,0.1,1.,10.], # H
        10. ** np.linspace(5, 6, 21),
        )
    inputs['f'], inputs['aspect'], inputs['H'], inputs['tauRef'] = \
        get_job(dims, SLICE, COUNTER, log=log)

    log("Creating final...")
    final = (
        planetengine.finals.Averages,
        {'tolerance': 1e-3, 'minlength': 100}
        )

    log("Creating system...")
    system = planetengine.systems.Viscoplastic(
        alpha = 1e7,
        res = 32,
        observers = True,
        innerMethod = 'lu',
        **inputs
        )

    log("Loading...")
    try:
        system.load('max')
    except ValueError:
        log("Failed. Initialising...")
        system.initialise()

    log("Running...")
    system[:final:100]()

    log("We did it!")


################################################################################
