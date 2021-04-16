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
    [float(a) for a in np.round(10 ** np.linspace(-2, 1, 13), 3)],
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

for i, alphaexp in enumerate(np.linspace(2.5, 7.5, 21)):

    alphaexp = float(alphaexp)

    system = System(
        alpha = 10. ** alphaexp,
        res = min(96, max(16, 2 ** round(alphaexp))),
        temperatureField = initial,
        **inputs
        )

    fig = QuickFig(
        system.locals.temperatureField,
        system.locals.velocityField,
        system.locals.viscosityFn,
        )

    args = [str(a).replace('.', ',') for a in [etaDelta, f, H, alphaexp]]
    figname = name + '_' + ';'.join(args)
    if not i:
        fig.save(figname + '_' + 'initial')

    system[:final:1000]()

    fig.save(figname + '_' + 'complete')

    if system.observers[0].analysers['Nu'].evaluate() < 1.001:
        initial = sinuinitial
    else:
        initial = system

################################################################################
