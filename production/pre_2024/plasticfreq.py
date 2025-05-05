import sys
import os
import math
import itertools
import numpy as np

ARG1 = int(sys.argv[1]) # geometry, 36 options
ARG2 = int(sys.argv[2]) # tauRef, 23 options
ARG3 = int(sys.argv[3]) # freqs, infinite options

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

from planetengine.systems import Viscoplastic as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal(freq = ARG3)
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

inputs = dict()
inputs['f'], inputs['aspect'] = list(itertools.product(
    np.linspace(0.5, 1.0, 6),
    [round(2. ** (i / 2), 3) for i in range(2)],
    ))[ARG1]
inputs['tauRef'] = [float(v) for v in 10. ** np.linspace(4.95, 6.05, 23)][ARG2]

system = System(
    alpha = 1e7,
    res = 64,
    observers = True,
    temperatureField = initial,
    innerMethod = 'lu',
    courant = 1.,
    **inputs
    )

system[:final:100]()
