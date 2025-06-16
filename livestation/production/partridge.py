################################################################################
''''''
################################################################################



import pickle
from pathlib import Path
import math

from everest.campaign import Job
from everest.disk import Locker

import planetengine
from planetengine.initials import *
from planetengine.systems import *

dims = dict(
    H=(0., 10**(-0.5), 1.), # H
    aspect=(1., 2**(0.5), 2.), # aspect
    etaDelta=(None, 1e1, 1e2, 1e3, 1e4, 3e4), # etaDelta
    f=(1., 0.9, 0.8, 0.7, 0.6, 0.5), # f
    flux=(None,), # flux
    )
defaults = dict(
    H=0.,
    aspect=1.,
    etaDelta=None,
    f=1.,
    flux=None,
    )
constants = dict()

with (
        Path(__file__).absolute().parent / 'simple_critical.data'
        ).open(mode='rb') as file:
    criticals = pickle.load(file)

initial = PostSinusoidal(factor=1.1, prior=Conductive())
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 100})

with Job(*(dims[key] for key in sorted(dims))) as job:

    log = job.log
    log("Starting...", "Setting up...")

    params = dict(zip(sorted(dims), job))
    for key, val in defaults.items():
        if key not in params:
            params[key] = val

    log("Params: ", params)

    alpha = criticals[tuple(params[key] for key in sorted(params))][-1] * 1 + 1e-5
    log("Initial alpha: " + str(alpha))

    if params['etaDelta'] is None:
        typ = Isovisc
        callparams = {**params}
        del callparams['etaDelta']
    else:
        typ = Arrhenius
        callparams = {**params}

    planetengine.set_global_anchor(job.campaignname, str(job.workdir))

    datafilepath = job.camproot.with_suffix('.data')

    log("Setup complete.", "Starting loop...")
    while True:

        if alpha > 1e7:
            alpha = 1e7

        log("Running alpha = " + str(alpha) + '...')

        alphaexp = math.ceil(math.log10(alpha))
        fineres = max(32, round(2 ** alphaexp / 4) * 4)
        coarseres = max(16, round(fineres // 2 / 4) * 4)

        log("Building coarse system...")
        coarsesystem = typ(
            alpha=alpha, res=coarseres, observers=True,
            temperatureField=initial,
            **callparams, **constants,
            )
        log("Coarse system built.", "Running coarse system...")
        coarsesystem[:final:100]()
        log("Coarse system complete.", "Building fine system...")
        finesystem = typ(
            alpha=alpha, res=fineres, observers=True,
            temperatureField=coarsesystem,
            **callparams, **constants,
            )
        log("Fine system built.", "Running fine system...")
        finesystem[:final:100]()
        log("Fine system complete.", "Completed alpha = " + str(alpha) + '.')

        log("Getting Nu value...")
        nuval = float(finesystem.observers[0].analysers['Nu'].evaluate())
        log("Nu = " + str(nuval), "Storing Nu value...")
        with Locker(str(datafilepath) + '.lock'):
            if datafilepath.exists():
                with datafilepath.open(mode='rb') as file:
                    stored = pickle.load(file)
            else:
                stored = {}
            stored[(*(params[key] for key in params), alpha)] = nuval
            with datafilepath.open(mode='wb') as file:
                pickle.dump(stored, file)
        log("Nu value stored.")

        if alpha >= 1e7:
            break

        alpha *= 2
        initial = finesystem

    log("Loop complete.", "We did it!")



################################################################################
################################################################################
