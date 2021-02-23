import sys
import os
arg = int(sys.argv[1])
tauRefs = [10 ** (i / 10) for i in range(49, 61)]
tauRef = tauRefs[arg]

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')
from planetengine.systems import Viscoplastic
from planetengine.initials import Sinusoidal
finalClass = planetengine.finals.Averages
finalInputs = {'tolerance': 1e-3, 'minlength': 50}
final = (finalClass, finalInputs)

initial = Sinusoidal(freq = 1.)
for aspect in [2 ** (i / 4) for i in range(7)]:
    system = Viscoplastic(
        res = 32,
        aspect = aspect,
        f = 1.,
        alpha = 10.**7.,
        tauRef = tauRef,
        observers = True,
        temperatureField = initial,
        innerMethod = 'lu',
        courant = 1.,
        )
    system[:final:100]()
    initial = system
