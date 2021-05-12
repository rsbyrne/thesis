################################################################################

import sys
import os
import math
import itertools

import numpy as np

ARG1, *ARGN = (None if arg == 'None' else int(arg) for arg in sys.argv[1:])

import planetengine
name = os.path.basename(__file__)[:-3]
planetengine.set_global_anchor(name, '.')

from planetengine.visualisation import QuickFig

inputs = dict(
    aspect = 1.,
    observers = True,
    innerMethod = 'lu',
    courant = 1.,
    )

etaDelta, f, H = list(itertools.product(
    [float(a) for a in np.round(10. ** np.linspace(0, 5, 11), 3)],
    [float(a) for a in np.round(np.linspace(1., 0.5, 11), 3)],
    [0., *[float(a) for a in np.round(10 ** np.linspace(-2, 1, 13), 3)]],
    ))[slice(*ARGN)][ARG1]

if etaDelta == 1:
    from planetengine.systems import Isovisc as System
else:
    from planetengine.systems import Arrhenius as System
    inputs['etaDelta'] = etaDelta

inputs['f'], inputs['H'] = f, H

from planetengine.initials import Sinusoidal
sinuinitial = Sinusoidal()
final = (
    planetengine.finals.Averages,
    {'tolerance': 1e-3, 'minlength': 100}
    )

initial = sinuinitial

alphaexp = 2
reinit = True

while alphaexp <= 7.:

    fine = max(8, round(2 ** alphaexp / 4) * 4)
    coarse = max(4, round(fine // 2 / 4) * 4)
    inputs['alpha'] = 10. ** alphaexp

    system = System(
        res = coarse,
        temperatureField = initial,
        **inputs
        )
    system[:final:1000]()

    system = System(
        res = fine,
        temperatureField = system,
        **inputs
        )
    system[:final:1000]()

    reinit = system.observers[0].analysers['Nu'].evaluate() < 1.001
    if reinit:
        initial = sinuinitial
    else:
        initial = system

    alphaexp = round(alphaexp + 0.1, 1)

################################################################################
