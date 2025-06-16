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

with Path('../simple_critical_all.data').open(mode='rb') as file:
    loaded = pickle.load(file)
def sortfn(params):
    out = []
    params = dict(params)
    for key in sorted(params):
        val = params[key]
        out.append(key)
        out.append(-1e12 if val is None else val)
    return tuple(out)
loaded = tuple((key, loaded[key]) for key in sorted(loaded, key=sortfn))

dims = dict(
    index=range(len(loaded)),
    none=(0,),
    )

stride = 1 + 1e-5
tolerance = 1e-6



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

def seek(checker, data, stride, tolerance):
    if not len(data):
        raise ValueError
    gen = converge(data.pop(), stride)
    data.append(gen.send(None))
    while len(data) < 2 or abs(data[-1] - data[-2]) / data[-1] > tolerance:
        data.append(gen.send(checker(data[-1])))
    return data[-1]


with Job(*(dims[key] for key in sorted(dims))) as job:

    log = job.log
    log("Starting...")

    index, _ = job
    params, data = loaded[int(index)]
    params = dict(params)
    data = list(data)
    log("Params:", params, "Data:", data)

    planetengine.set_global_anchor(job.campaignname, str(job.workdir))

    def checker(val):
        if not 0. < val < 1e5:
            raise ValueError
        log("Trying alpha: " + str(val))
        if params['etaDelta'] is None:
            typ = Isovisc
            callparams = {**params}
            del callparams['etaDelta']
        else:
            typ = Arrhenius
            callparams = {**params}
        system = typ(
            alpha=val, res=32, observers=True,
            temperatureField=initial,
            **callparams,
            )
        val0 = system.observers[1].analysers['VRMS'].evaluate()
        log("Initial VRMS: " + str(val0))
        system[:final]()
        system.store()
        system.save()
        val1 = system.observers[1].analysers['VRMS'].evaluate()
        log("Final VRMS: " + str(val1))
        return val1 / val0 < 1

    val = seek(checker, data, stride, tolerance)

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