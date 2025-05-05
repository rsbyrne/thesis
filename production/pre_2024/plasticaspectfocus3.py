import sys
import os
import numpy as np

ARG1 = int(sys.argv[1]) # f, 6 options
ARG2 = int(sys.argv[2]) # tauRef, 4 options
ARG3 = int(sys.argv[3]) # aspect, 9 options

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

from planetengine.systems import Viscoplastic as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal(freq = 1)
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

inputs = dict()
inputs['f'] = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0][ARG1]
inputs['tauRef'] = (10. ** np.linspace(5.9, 6.05, 4))[ARG2]
inputs['aspect'] = [float(i) for i in np.round(2. ** np.linspace(0, 0.5, 11), 3)][1:-1][ARG3]

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
