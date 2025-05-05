################################################################################

import sys
import os
import math

import numpy as np

ARG1 = int(sys.argv[1]) # curvature, 5 options
ARG2 = int(sys.argv[2]) # heating, 10 options
ARG3 = int(sys.argv[3]) # tauRef, 11 options

import planetengine
name = os.path.basename(__file__)[:-3]
planetengine.set_global_anchor(name, '.')

inputs = dict(
    observers = True,
    innerMethod = 'mg',
    courant = 1.,
    )
f = inputs['f'] = float(np.linspace(0.9, 0.5, 5)[ARG1])
H = inputs['H'] = [0., *[10. ** (i / 4) for i in range(-4, 5)]][ARG2]

from planetengine.systems import Isovisc, Arrhenius, Viscoplastic
from planetengine.initials import Sinusoidal, Copy
from planetengine.visualisation import QuickFig

final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 100})

def get_aspect(f):
    outer = 1 / (1 - f)
    inner = outer - 1
    full = math.pi * (outer + inner)
    cycles = round(full / 2) * 2
    partial = round(full / cycles, 3)
    return cycles, partial
cycles, partial = get_aspect(f)

# ISOVISC

isovisc = Isovisc(
    temperatureField = Sinusoidal(),
    alpha = 1e5,
    aspect = partial,
    res = 32,
    **inputs
    )
isovisc[:final:100]()

# ARRHENIUS

inputs['etaDelta'] = 3e4
inputs['alpha'] = 1e7

arrhenius = Arrhenius(
    temperatureField = isovisc,
    aspect = partial,
    res = 64,
    **inputs
    )

arrfull = Arrhenius(
    temperatureField = Copy(
        arrhenius[:final:100],
        'temperatureField',
        mirrored = (True, False),
        tiles = (cycles / 2, 1),
        ),
    res = 32,
    **inputs
    )

arrfull[:final:100]()

arrtempered = Arrhenius(
    temperatureField = arrfull,
    res = 64,
    **inputs
    )

arrtempered[:final:100]()

# LOW-RES VISCOPLASTIC

tauRef = inputs['tauRef'] = float((10. ** np.linspace(5, 6, 11))[ARG3])
inputs['aspect'] = 'max'

args = [str(a).replace('.', ',') for a in [f, H, tauRef]]
figname = name + '_' + '-'.join(args)
def make_fig(system):
    return QuickFig(
        system.locals.temperatureField,
        system.locals.velocityField,
        system.locals.viscosityFn,
        )

system = Viscoplastic(
    temperatureField = arrtempered,
    res = 32,
    **inputs
    )
fig = make_fig(system)

system.initialise()
fig.save(figname + '_' + 'preview')
system[:final:100]()
fig.save(figname + '_' + 'complete')

# HIGH-RES VISCOPLASTIC

tempered = Viscoplastic(
    temperatureField = system,
    res = 64,
    **inputs
    )
fig = make_fig(tempered)

tempered.initialise()
fig.save(figname + '_' + 'tempered' + '_' + 'preview')
tempered[:final:100]()
fig.save(figname + '_' + 'tempered' + '_' + 'complete')

################################################################################
