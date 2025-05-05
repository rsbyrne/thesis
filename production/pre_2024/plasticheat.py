################################################################################

import sys
import os
import math
import itertools
import numpy as np

ARG1 = int(sys.argv[1]) # geometry, 36 options
ARG2 = int(sys.argv[2]) # tauRef, 23 options
ARG3 = int(sys.argv[3]) # heating, 10 options
# ARG4 = int(sys.argv[3]) # freqs, infinite options

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

from planetengine.systems import Viscoplastic as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal(freq = 1.)
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

inputs = dict()
inputs['f'], inputs['aspect'] = (float(v) for v in list(itertools.product(
    np.linspace(1.0, 0.5, 6),
    np.round(2 ** np.linspace(0, 0.5, 6), 3),
    ))[ARG1])
inputs['tauRef'] = float((10. ** np.linspace(4.95, 6.05, 23))[ARG2])
inputs['H'] = [0., *[10. ** (i / 4) for i in range(-4, 5)]][ARG3]

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
