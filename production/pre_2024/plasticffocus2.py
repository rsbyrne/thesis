import sys
import os
import numpy as np

ARG1 = int(sys.argv[1]) # aspect, 2 options
ARG2 = int(sys.argv[2]) # tauRef, 12 options
ARG3 = int(sys.argv[3]) # f, 9 options

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

from planetengine.systems import Viscoplastic as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal(freq = 1)
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

inputs = dict()
inputs['aspect'] = [1., 1.414][ARG1]
inputs['tauRef'] = (10. ** (np.linspace(5.3, 5.85, 12), np.linspace(5.5, 6.05, 12))[ARG1])[ARG2]
inputs['f'] = [float(v) for v in [*np.linspace(0.72, 0.78, 4), *np.linspace(0.55, 0.95, 5)]][ARG3]

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
