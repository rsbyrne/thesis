import sys
import os
import math
import itertools
import numpy as np

ARG1 = int(sys.argv[1]) # tauRefs, freqs, fs, aspects; 12 options
inputs = dict()
inputs['tauRef'], freq, inputs['f'], inputs['aspect'] = list(itertools.product(
    [10 ** i for i in np.linspace(5, 6, 6)],
    [1.,],
    [0.5, 1.0],
    [1.,],
    ))[ARG1]

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

from planetengine.systems import Viscoplastic as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal(freq = freq)
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

system = System(
    alpha = 1e7,
    res = 128,
    observers = True,
    temperatureField = initial,
    innerMethod = 'lu',
    courant = 1.,
    **inputs
    )

system[:final:100]()
