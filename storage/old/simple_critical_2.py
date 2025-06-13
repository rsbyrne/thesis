################################################################################
''''''
################################################################################



import pickle
from pathlib import Path

from everest.campaign import Job
from everest.disk import Locker

import planetengine
from planetengine.initials import *
from planetengine.systems import *



dims = dict(
    f = tuple(val / 10 for val in range(10, 2, -1)),
    aspect = tuple(2.**(val / 10) for val in range(0, 11)),
    etaDelta = tuple(10.**val for val in range(-5, 6)),
#     H = tuple(10.**(val / 10) for val in range(-10, 11, 2)),
    )
constants = dict(
#     flux=0.,
    )
prior = 800.
optimism = 1.
tolerance = 1e-5



initial = PostSinusoidal(factor=1.1, prior=Conductive())
final = 0.1



def convergence(val, optimism=10.):
    is_too_low = yield val
    if is_too_low:
        incrementer = 1
        while is_too_low:
            lbnd = val
            val *= 2**(incrementer / optimism)
            incrementer += 1
            is_too_low = yield val
        ubnd = val
    else:
        incrementer = 1
        while not is_too_low:
            ubnd = val
            val /= 2**(incrementer / optimism)
            incrementer += 1
            is_too_low = yield val
        lbnd = val
    is_too_low = True
    val = lbnd
    while True:
        assert ubnd > lbnd, (lbnd, ubnd)
        while is_too_low:
            lbnd = val
            diff = ubnd - lbnd
            val += diff / 2
            is_too_low = yield val
        ubnd = val
        while not is_too_low:
            ubnd = val
            diff = ubnd - lbnd
            val -= diff / 2
            is_too_low = yield val
        lbnd = val



with Job(*(dims[key] for key in sorted(dims))) as job:

    log = job.log
    log("Starting...")

    params = dict(zip(sorted(dims), job))

    planetengine.set_global_anchor(job.campaignname, str(job.workdir))

    def checker(val):
        if not 0. < val < 1e5:
            raise ValueError
        log("Trying alpha: " + str(val))
        system = Arrhenius(
            alpha=val, res=32, observers=True,
            temperatureField=initial,
            **params, **constants,
            )
        val0 = system.observers[1].analysers['VRMS'].evaluate()
        log("Initial VRMS: " + str(val0))
        system[:final]()
        system.store()
        system.save()
        val1 = system.observers[1].analysers['VRMS'].evaluate()
        log("Final VRMS: " + str(val1))
        return val1 / val0 < 1

    gen = convergence(prior, optimism=optimism)
    data = [gen.send(None)]

    while len(data) < 2 or abs(data[-1] - data[-2]) / data[-1] > tolerance:
        data.append(gen.send(checker(data[-1])))

    log("Converged.", "Saving...", data)

    datafilepath = job.camproot.with_suffix('.data')
    with Locker(str(datafilepath) + '.lock'):
        if datafilepath.exists():
            with datafilepath.open(mode='rb') as file:
                stored = pickle.load(file)
        else:
            stored = {}
        stored[tuple(params[key] for key in sorted(params))] = tuple(data)
        with datafilepath.open(mode='wb') as file:
            pickle.dump(stored, file)

    log("We did it!")



################################################################################
################################################################################
