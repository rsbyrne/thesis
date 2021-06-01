import pickle

import numpy as np

from planetengine.systems import Isovisc
from planetengine import quickShow
from planetengine.visualisation import QuickFig
from planetengine import functions as pfn

hs = np.concatenate((np.linspace(0., 1.0, 6), np.linspace(2., 12., 6)))
fs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

geotherms = []
condavts = []
hfs = []
for f in fs:
    for h in hs:
        hfs.append((h, f))
        system = Isovisc(alpha = 1., f = f, H = h, res = 64)
        system.initialise()
        temp = system.locals.temperatureField
        diff = system.locals.diffusivityFn
        cond = pfn.conduction.default(temp, h, diff)
        condavt = pfn.integral.volume(cond).data
        left = pfn.surface.left(cond)
#        fig = QuickFig(cond, background = 'white', edgecolour = 'white')
#         fig.show()
        geotherms.append(left.data)
        condavts.append(condavt)
#        fig.save('cond_hf_mixed_' + str(h).replace('.', '-') + '_' + str(f).replace('.', '-'))

out = {
    'hfs': hfs,
    'geotherms': geotherms,
    'avts': condavts,
    }

with open('condhfmixed.pkl', mode = 'wb') as file:
    file.write(pickle.dumps(out))
