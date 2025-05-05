################################################################################

import os

import planetengine
name = os.path.basename(__file__)[:-3]
planetengine.set_global_anchor(name, '.')

from planetengine.systems import Isovisc
from planetengine.initials import Sinusoidal
from planetengine.visualisation import QuickFig

final = (planetengine.finals.Averages, {'tolerance': 1e-2, 'minlength': 50})

system = Isovisc(
    observers = True,
    innerMethod = 'mg',
    aspect = 'max',
    alpha = 1e6,
    f = 0.5,
    res = 32,
    temperatureField = Sinusoidal(freq = 10),
    )

system.initialise()

fig = QuickFig(
    system.locals.temperatureField,
    system.locals.velocityField,
    system.locals.viscosityFn,
    )

fig.save(name + '_' + str(ARG1) + '_' + str(ARG2) + '_' + 'preview')

system[:final:30]()

fig.save(name + '_' + str(ARG1) + '_' + str(ARG2) + '_' + 'complete')

################################################################################