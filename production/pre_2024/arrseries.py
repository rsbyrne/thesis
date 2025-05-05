import sys
import os
import itertools
ARG1 = int(sys.argv[1])
ARG2 = int(sys.argv[2])

etaDelta = [10 ** (i / 2) for i in range(1, 13)][ARG1]
f, aspect = list(itertools.product(
    [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    [2 ** (i / 2) for i in range(-1, 3)],
    ))[ARG2]

import math
import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')
from planetengine.systems import Arrhenius
from planetengine.initials import Sinusoidal

initial = Sinusoidal()
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})
for alpha in [10 ** (i / 4.) for i in range(16, 29)]:
    system = Arrhenius(
        f = f,
        aspect = aspect,
        res = 2 ** math.ceil(math.log10(alpha)),
        alpha = alpha,
        observers = True,
        temperatureField = initial,
        innerMethod = 'lu',
        courant = 1.,
        )
    system[:final:1000]()
    initial = system
