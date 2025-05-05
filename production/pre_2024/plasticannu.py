################################################################################

import sys
import os
import math

import numpy as np

ARG1 = int(sys.argv[1]) # curvature, 5 options
ARG2 = int(sys.argv[2]) # tauRef, 11 options

import planetengine
name = os.path.basename(__file__)[:-3]
planetengine.set_global_anchor(name, '.')

inputs = dict(
    observers = True,
    innerMethod = 'mg',
    courant = 1.,
    )
f = inputs['f'] = float(np.linspace(0.9, 0.5, 5)[ARG1])

from planetengine.systems import Isovisc, Arrhenius, Viscoplastic
from planetengine.initials import Sinusoidal, Copy
from planetengine.visualisation import QuickFig

final = (planetengine.finals.Averages, {'tolerance': 1e-2, 'minlength': 50})

def get_aspect(f):
    outer = 1 / (1 - f)
    inner = outer - 1
    full = math.pi * (outer + inner)
    cycles = round(full / 2) * 2
    partial = round(full / cycles, 3)
    return cycles, partial
cycles, partial = get_aspect(f)

isovisc = Isovisc(
    temperatureField = Sinusoidal(),
    alpha = 1e5,
    aspect = partial,
    res = 32,
    **inputs
    )
isotraverse = isovisc[:final:100]

inputs['etaDelta'] = 3e4
inputs['alpha'] = 1e7

arrhenius = Arrhenius(
    temperatureField = isotraverse,
    aspect = partial,
    res = 64,
    **inputs
    )

arrtraverse = arrhenius[:final:100]

inputs['tauRef'] = float((10. ** np.linspace(5, 6, 11))[ARG2])

system = Viscoplastic(
    temperatureField = Copy(
        arrtraverse,
        'temperatureField',
        mirrored = (True, False),
        tiles = (cycles / 2, 1),
        ),
    aspect = 'max',
    res = 32,
    **inputs
    )

system.initialise()

fig = QuickFig(
    system.locals.temperatureField,
    system.locals.velocityField,
    system.locals.viscosityFn,
    )

fig.save(name + '_' + str(ARG1) + '_' + str(ARG2) + '_' + 'preview')

system[:final:50]()

fig.save(name + '_' + str(ARG1) + '_' + str(ARG2) + '_' + 'complete')

################################################################################
