import sys
import os
arg = int(sys.argv[1])
tauRef = [(i / 20) for i in range(100, 121)][arg] # 21 cases

import math
import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')
from planetengine.systems import Arrhenius, Viscoplastic
from planetengine.initials import Sinusoidal
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

initial = Sinusoidal(freq = 1.)
for alpha in [10 ** (i / 2.) for i in range(8, 15)]:
    system = Arrhenius(
        f = 1.,
        aspect = 1.,
        res = min(64, 2 ** math.floor(math.log10(alpha))),
        alpha = alpha,
        observers = True,
        temperatureField = initial,
        innerMethod = 'lu',
        courant = 1.,
        )
    system[:final]()
    initial = system

system = Viscoplastic(
    f = 1.,
    aspect = 1.,
    res = 64,
    alpha = 10.**7.,
    tauRef = tauRef,
    observers = True,
    temperatureField = initial,
    innerMethod = 'lu',
    courant = 1,
    )
system[:final:100]()
