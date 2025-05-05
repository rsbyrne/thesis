import sys
import os
arg = int(sys.argv[1])
tauRefs1 = [10 ** (i / 10) for i in range(49, 61)]
tauRefs2 = [10 ** round((i / 10 + 0.05), 2) for i in range(49, 61)]
tauRef1 = tauRefs1[arg]
tauRef2 = tauRefs2[::-1][arg]

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')
from planetengine.systems import Isovisc, Viscoplastic
from planetengine.initials import Sinusoidal
finalClass = planetengine.finals.Averages
finalInputs = {'tolerance': 1e-3, 'minlength': 50}
final = (finalClass, finalInputs)
inputs = {'f': 1., 'aspect': 0.707, 'innerMethod': 'lu', 'courant': 1.}

for tauRef in (tauRef1, tauRef2):
    system = Viscoplastic(
        res = 64,
        alpha = 10.**7.,
        tauRef = tauRef,
        observers = True,
        temperatureField = Sinusoidal(freq = 1.),
        **inputs
        )
    system[:final:100]()
