###############################################################################
''''''
###############################################################################



filename = 'alphacrit_aspect_h_f03.pkl'
outerkey, outervals = 'aspect', [2.**(val / 10) for val in range(0, 11)]
innerkey, innervals = 'H', [10.**(val / 10) for val in range(-10, 11)][::2]
constants = dict(f=0.3)
prior = 800.
optimism = 5.



###############################################################################
###############################################################################



import os
import pickle
import time

from planetengine import set_global_anchor
from planetengine.systems import *
from planetengine.initials import *

outdir = '/home/jovyan/workspace/data'



logfile = os.path.join('.', filename.split('.')[0]+'.log')
with open(logfile, mode='w') as file:
    file.write(logfile + '\n')
def log(text):
    with open(logfile, mode='a') as file:
        file.write('\n' + str(time.time()) + '\n' + str(text) + '\n')



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



def get_checker(**params):
    def checker(val):
        if not 0. < val < 1e5:
            raise ValueError
        log("Trying alpha: " + str(val))
        system = Isovisc(
            alpha=val, res=32, observers=True,
            temperatureField=PostSinusoidal(factor=1.1, prior=Conductive()),
            **params,
            )
        val0 = system.observers[1].analysers['VRMS'].evaluate()
        log("Initial VRMS: " + str(val0))
        system[:0.1]()
        system.store()
        system.save()
        val1 = system.observers[1].analysers['VRMS'].evaluate()
        log("Final VRMS: " + str(val1))
        return val1 / val0 < 1
    return checker



set_global_anchor('simple_critical', outdir)

alldatas = {}

for outerval in outervals:

    datas = alldatas[outerval] = {}

    for innerval in innervals:

        checker = get_checker(
            **{outerkey: outerval, innerkey: innerval},
            **constants,
            )
        gen = convergence(prior, optimism=optimism)
        data = datas[innerval] = [gen.send(None)]
        while len(data) < 2 or abs(data[-1] - data[-2]) / data[-1] > 1e-5:
            data.append(gen.send(checker(data[-1])))

        prior = data[-1]
        optimism = 50.
        log(data)
        with open(os.path.join(outdir, filename), mode='wb') as file:
            pickle.dump(alldatas, file)



###############################################################################



# gen = convergence(877.787745)
# testdata = [gen.send(None)]
# check = lambda x: x < 851.370284
# for _ in range(15):
#     testdata.append(gen.send(check(testdata[-1])))
# testdata



###############################################################################
