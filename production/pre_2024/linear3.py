################################################################################
################################################################################


import sys
import os
import math
import itertools

import numpy as np

import planetengine

from campaign import get_job, get_logger


CAMPAIGNNAME, LOGPATH, COUNTER, *SLICE = sys.argv[1:]

planetengine.set_global_anchor(CAMPAIGNNAME, '.')

with open(LOGPATH, mode = 'r+') as logfile:

    log = get_logger(logfile)

    log(CAMPAIGNNAME, LOGPATH, ', '.join(SLICE), COUNTER)

    inputs = dict(
        observers = True,
        innerMethod = 'lu',
        courant = 1.,
        )
    dims = (
        np.round(10. ** np.linspace(0, 5, 11), 3), # etaDelta
        np.round(np.linspace(1., 0.5, 11), 3), # f
        np.round(2. ** np.linspace(0, 1, 11), 3), # aspect
        np.array([0., *np.round(10 ** np.linspace(-2, 1, 13), 3)]), # H
        )
    etaDelta, f, aspect, H = get_job(dims, SLICE, COUNTER, log=log)
    if etaDelta == 1:
        from planetengine.systems import Isovisc as System
    else:
        from planetengine.systems import Arrhenius as System
        inputs['etaDelta'] = etaDelta
    inputs['f'], inputs['aspect'], inputs['H'] = f, aspect, H

    from planetengine.initials import Sinusoidal
    sinuinitial = Sinusoidal()
    final = (
        planetengine.finals.Averages,
        {'tolerance': 1e-3, 'minlength': 100}
        )

    initial = sinuinitial

    alphaexp = 2
    reinit = True

    log("Here we go...")

    while alphaexp <= 7.:

        log("Starting alphaexp=" + str(alphaexp) + '...')

        fine = max(8, round(2 ** alphaexp / 4) * 4)
        coarse = max(4, round(fine // 2 / 4) * 4)
        inputs['alpha'] = 10. ** alphaexp

        log("Coarse-resolution=" + str(coarse) + "...")
        system = System(
            res = coarse,
            temperatureField = initial,
            **inputs
            )
        system[:final:1000]()
        log("Complete.")

        log("Fine-resolution=" + str(fine) + "...")
        system = System(
            res = fine,
            temperatureField = system,
            **inputs
            )
        system[:final:1000]()
        log("Complete.")

        log("Completed alphaexp=" + str(alphaexp) + '.')

        reinit = system.observers[0].analysers['Nu'].evaluate() < 1.001
        if reinit:
            initial = sinuinitial
        else:
            initial = system

        alphaexp = round(alphaexp + 0.1, 1)

    log("We did it!")


################################################################################
################################################################################
