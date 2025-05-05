import sys
import os
arg = int(sys.argv[1])

import numpy as np

f = 1.
aspect = 1.
freq = 1.
tauBounds = {
    (0.5, 1, 1): ((5.5, 5.55), (5.75, 5.8)),
    (0.6, 1, 1): ((5.45, 5.5), (5.75, 5.8)),
    (0.7, 1, 1): ((5.45, 5.5), (5.75, 5.8)),
    (0.8, 1, 1): ((5.4, 5.45), (5.7, 5.75)),
    (0.9, 1, 1): ((5.35, 5.4), (5.7, 5.75)),
    (1.0, 1, 1): ((5.35, 5.4), (5.7, 5.75)),
    }[f, aspect, freq]
tauExps = []
for l, u in tauBounds:
    tauExps.extend(round(v, 2) for v in np.linspace(l, u, num = 6)[1:-1])
tauExp = tauExps[arg]
tauRef = 10. ** tauExp

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')
from planetengine.systems import Isovisc, Viscoplastic
from planetengine.initials import Sinusoidal
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

system = Viscoplastic(
    res = 64,
    f = f,
    aspect = aspect,
    innerMethod = 'lu',
    courant = 1.,
    alpha = 10.**7.,
    tauRef = tauRef,
    observers = True,
    temperatureField = Sinusoidal(freq = freq),
    )
system[:final:100]()
