################################################################################

import sys
import os
import math
import itertools
import numpy as np

ARG1, *ARGN = (None if arg == 'None' else int(arg) for arg in sys.argv[1:])

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

from planetengine.systems import Viscoplastic as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal(freq = 1.)
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

options = list(itertools.product(
    [float(v) for v in np.linspace(1.0, 0.5, 6)],
    [float(v) for v in np.round(2 ** np.linspace(0, 0.5, 6), 3)],
    [0., *[10. ** (i / 4) for i in range(-4, 5)]],
    [float(v) for v in (10. ** np.linspace(4.95, 6.05, 23))],
    ))
inputs = dict()
inputs['f'], inputs['aspect'], inputs['H'], inputs['tauRef'] = options[slice(*ARGN)][ARG1]

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

################################################################################
