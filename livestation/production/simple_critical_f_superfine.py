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
    f=tuple(
        val for val in tuple(val / 100 for val in range(100, 50, -1))
        if val not in tuple(val / 20 for val in range(20, 9, -1))
        ),
    aspect = (1., 2**0.5, 2),
#     etaDelta = tuple(10.**(val+0.5) for val in range(-4, 5)),
#     H = tuple(10.**(val / 2) for val in range(-2, 3)),
    )
constants = dict(
#     flux=0.,
#     H=1.,
    )
prior = 1000.
stride = 2.
tolerance = 1e-5



initial = PostSinusoidal(factor=1.1, prior=Conductive())
final = 0.1



def converge(prior, stride=2.):
    val = prior
    is_too_low = yield val
    if is_too_low:
        while is_too_low:
            lbnd = val
            val *= stride
            is_too_low = yield val
        ubnd = val
    else:
        while not is_too_low:
            ubnd = val
            val /= stride
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

def seek(checker, prior, stride, tolerance, data=None):
    gen = converge(prior, stride)
    if data is None:
        data = []
    data.append(gen.send(None))
    while len(data) < 2 or abs(data[-1] - data[-2]) / data[-1] > tolerance:
        data.append(gen.send(checker(data[-1])))
    return data[-1]


with Job(*(dims[key] for key in sorted(dims))) as job:

    log = job.log
    log("Starting...")

    params = dict(zip(sorted(dims), job))

    planetengine.set_global_anchor(job.campaignname, str(job.workdir))

    def checker(val):
        if not 0. < val < 1e6:
            raise ValueError
        log("Trying alpha: " + str(val))
        system = Isovisc(
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

    data = []
    val = seek(checker, prior, stride, tolerance, data)

    log("Converged.", val, "Saving...", data)

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
