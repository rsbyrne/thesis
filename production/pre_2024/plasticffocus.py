import sys
import os
import numpy as np

ARG1 = int(sys.argv[1]) # tauRef, 12 options
ARG2 = int(sys.argv[2]) # geometry, 4 options

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

from planetengine.systems import Viscoplastic as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal(freq = 1)
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

inputs = dict()
inputs['tauRef'] = (10. ** np.linspace(5.3, 5.85, 12))[ARG1]
inputs['f'] = np.linspace(0.7, 0.8, 6)[1:-1][ARG2]

system = System(
    alpha = 1e7,
    aspect = 1.,
    res = 64,
    observers = True,
    temperatureField = initial,
    innerMethod = 'lu',
    courant = 1.,
    **inputs
    )

system[:final:100]()
